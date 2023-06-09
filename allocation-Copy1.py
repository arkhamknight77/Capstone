#!/usr/bin/env python
# coding: utf-8

# In[212]:


pip install fredapi


# In[213]:


from fredapi import Fred
import pandas as pd
pd.options.mode.chained_assignment = None

from collections import defaultdict
from datetime import datetime
from dateutil.relativedelta import relativedelta
import numpy as np
import pickle

from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import fbeta_score, roc_curve, roc_auc_score, accuracy_score, precision_score
from sklearn.metrics import recall_score, make_scorer
from sklearn.metrics import confusion_matrix

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import seaborn as sns
import ast

import warnings
import sklearn.exceptions as sklearn_except

get_ipython().run_line_magic('matplotlib', 'inline')


# In[214]:


path = "C:/Users/Jeetesh/CAPSTONEEEE/CAPSTONE ALLOCATION/graphs/"


# In[215]:


fred = Fred(api_key="373c1ab63543a01b4a3e5471bfa4b524")

T10Y3M = pd.Series(fred.get_series("T10Y3M"), name="T10Y3M")
unrate = pd.Series(fred.get_series("UNRATE"), name = "UNRATE")
NFCI = pd.Series(fred.get_series("NFCINONFINLEVERAGE"), name="NFCI")
us_rec = pd.Series(fred.get_series("USREC"), name="USREC")
DGS10 = pd.Series(fred.get_series("DGS10"), name="DGS10")
CPI = pd.Series(fred.get_series("CPIAUCSL"), name="CPI")


# In[216]:


fig, axs = plt.subplots(2,3, figsize=(20,10), gridspec_kw = {"hspace":0.3})

axs[0][0].plot(T10Y3M)
axs[0][0].set_title("10YR - 3M Spread", weight="bold")

axs[0][1].plot(unrate)
axs[0][1].set_title("Unemployment Rate (U3)", weight="bold")

axs[0][2].plot(NFCI)
axs[0][2].set_title("NFCI", weight="bold")

# Recession data goes back to 1854, limit to more recent history
axs[1][0].plot(us_rec.loc[us_rec.index.year>=1950])
axs[1][0].set_title("NBER Recession Indicator", weight="bold")

axs[1][1].plot(DGS10)
axs[1][1].set_title("10-yr Constant Maturity Yield", weight="bold")

axs[1][2].plot(CPI)
axs[1][2].set_title("CPI", weight="bold");


# In[217]:


df = pd.concat([T10Y3M, NFCI, unrate, us_rec, DGS10, CPI], axis=1)


# In[218]:


df


# In[ ]:





# In[ ]:





# In[ ]:





# In[219]:


year_month = pd.Series([str(x) for x in df.index.year.values]) + "-" + pd.Series([str(x) for x in df.index.month.values])
df["year_month"] = year_month.values

df = df.groupby("year_month")[["T10Y3M", "UNRATE", "NFCI", "USREC", "DGS10", "CPI"]].mean().dropna()


# In[220]:


df.head()


# In[221]:


df.index = pd.to_datetime(df.index)
df.sort_index(inplace=True)
df.index.name = None


# In[222]:


df["CPI_chg"] = df["CPI"].pct_change()


# In[223]:


df.head()


# In[ ]:





# In[ ]:





# In[ ]:





# In[224]:


SP500 = pd.read_csv("com.csv", index_col=0, header=0, names=["S&P500","divs_annualized"])


# In[ ]:





# In[225]:


df = df.join(SP500)


# In[226]:


df.head()


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[227]:


df["divs_monthly"] = df["divs_annualized"] / 12
df["S&P500_total_return"] = (df["S&P500"] + df["divs_monthly"]) / df["S&P500"].shift(1) - 1
df["real_S&P500_total_return"] = df["S&P500_total_return"] - df["CPI_chg"]


# In[228]:


term = (df.index.max() - df.index.min()).days/365
print("S&P500 CAGR:",round((np.prod(df["S&P500_total_return"]+1)**(1/term) - 1)*100,2),"%")


# In[229]:


df["DGS10_prior"] = df["DGS10"].shift(1, fill_value=0)


# In[230]:


df["treasury_return"] = (df["DGS10_prior"]/100*(1 - 1/(1 + df["DGS10"]/100)**10))/(df["DGS10"]/100) +                                            1/(1 + df["DGS10"]/100)**10 - 1 + df["DGS10_prior"]/100/12


# In[231]:


df.head()


# In[232]:


df["real_treasury_return"] = df["treasury_return"] - df["CPI_chg"]

df["treasury_return"].iloc[0]=0
df["real_treasury_return"].iloc[0]=0


# In[233]:


df["rel_treasury_return"] = 1 + df["treasury_return"]
print((df.groupby(df.index.year)["rel_treasury_return"].prod()-1))
print("")
print(f"10-YR Treasury CAGR {df.index.min().year}-{df.index.max().year}:", np.prod(df["treasury_return"]+1)**(1/term)-1)


# In[ ]:





# In[ ]:





# In[ ]:





# In[234]:


df["USREC_shifted"] = df["USREC"].shift(-12, fill_value=0)

df[["USREC","USREC_shifted"]].iloc[-50:-35]


# In[235]:


df_SMA = df.copy()


# In[236]:


df_SMA["T10Y3M_SMA"] = df_SMA["T10Y3M"].rolling(3).mean() 
df_SMA["UNRATE_SMA"] = df_SMA["UNRATE"].rolling(3).mean()
df_SMA["NFCI_SMA"] = df_SMA["NFCI"].rolling(3).mean()


df_SMA.dropna(inplace=True)


# In[237]:


df_SMA.head()


# In[ ]:





# In[ ]:





# In[ ]:





# In[238]:


train_split = "2001-11-01"
train_split = datetime(int(train_split[0:4]), int(train_split[5:7]), int(train_split[9:11]))


# In[239]:


plt.figure(figsize=(10,5))
plt.plot(df_SMA.index, df_SMA["T10Y3M_SMA"], label="T10Y3M")
plt.plot(df_SMA["UNRATE_SMA"], label="UNRATE")
plt.plot(df_SMA["NFCI_SMA"], label="NFCI")
plt.legend(ncol=3, bbox_to_anchor=(0.70,-0.08), prop={"size": 10})
plt.ylabel("Feature values")
plt.axvline(train_split,color="r", linestyle="--")

ax1 = plt.twinx()
ax1.plot(df_SMA["USREC"], "lightgray", label="USREC")
ax1.fill_between(df_SMA.index,df_SMA["USREC"],color="lightgray",alpha=0.15)
ax1.get_yaxis().set_visible(False)

plt.savefig(path +"train_test_split.png", dpi=300);


# In[240]:


T10Y3M_0 = df_SMA[df_SMA["USREC_shifted"]==0]["T10Y3M_SMA"]
T10Y3M_1 = df_SMA[df_SMA["USREC_shifted"]==1]["T10Y3M_SMA"]

UNRATE_0 = df_SMA[df_SMA["USREC_shifted"]==0]["UNRATE_SMA"]
UNRATE_1 = df_SMA[df_SMA["USREC_shifted"]==1]["UNRATE_SMA"]

NFCI_0 = df_SMA[df_SMA["USREC_shifted"]==0]["NFCI_SMA"]
NFCI_1 = df_SMA[df_SMA["USREC_shifted"]==1]["NFCI_SMA"]


# In[241]:


fig, axs = plt.subplots(1,3, figsize=(15,4))
sns.distplot(T10Y3M_0, hist=False, ax=axs[0], label="Expansion")
sns.distplot(T10Y3M_1, hist=False, ax=axs[0], label="Recession")
axs[0].set_title("10YR - 3M Spread", weight="bold")
axs[0].legend()

sns.distplot(UNRATE_0, hist=False, ax=axs[1], label="Expansion")
sns.distplot(UNRATE_1, hist=False, ax=axs[1], label="Recession")
axs[1].set_title("Unemployment Rate", weight="bold")

sns.distplot(NFCI_0, hist=False, ax=axs[2], label="Expansion")
sns.distplot(NFCI_1, hist=False, ax=axs[2], label="Recession")
axs[2].set_title("Non-Financial Leverage", weight="bold")

plt.savefig(path + "distplot.png", dpi=300);


# In[242]:


#print("Recessions account for:", "{:.1f}".format(df["USREC"].value_counts()[1]/df["USREC"].value_counts()[0]*100),"% of observations")


# In[ ]:





# In[ ]:





# In[243]:


avg_exp_ret = df[df["USREC"] == 0]["S&P500_total_return"].mean()
avg_rec_ret = df[df["USREC"] == 1]["S&P500_total_return"].mean()

print(f"The S&P500 has mean monthly returns of {avg_exp_ret*100:.3f}% in expansions and mean monthly returns of {avg_rec_ret*100:.3f}% in recessions.")
beta = -avg_rec_ret / avg_exp_ret
print(f"Beta: {beta:.3f}")


# In[ ]:





# In[ ]:





# In[ ]:





# In[244]:


X = df_SMA[["T10Y3M_SMA","UNRATE_SMA","NFCI_SMA"]]
y = df_SMA["USREC_shifted"]


# In[245]:


X_train = X[X.index <= train_split]
y_train = y[y.index <= train_split]
X_test = X[X.index > train_split]
y_test = y[y.index > train_split]


scaler = StandardScaler()
X_train_lr = scaler.fit_transform(X_train)
X_test_lr = scaler.transform(X_test)


# In[246]:


warnings.filterwarnings("ignore", category=sklearn_except.UndefinedMetricWarning)


class_weights = [{0:weight, 1:1-weight} for weight in np.arange(0.05,1,0.05)]


first_rec = y_train[y_train.index=="1989-12-01"].index[0]
num_years = int((train_split-first_rec).days/365)

train_dates = [first_rec]+[first_rec + relativedelta(months=+12) * i for i in range(1,num_years)]

fbeta_dict = defaultdict(list)
for date in train_dates:
        X_train_cv = X_train[X_train.index <= date]
        y_train_cv = y_train[y_train.index <= date]
        X_test_cv = X_train[date+relativedelta(months=+1) : date + relativedelta(months=+12)]
        y_test_cv = y_train[date+relativedelta(months=+1) : date + relativedelta(months=+12)]
        
        for weight in class_weights:
            logistic_regression = LogisticRegression(random_state=4, class_weight=weight)
            logistic_regression.fit(X_train_cv, y_train_cv)
            preds = logistic_regression.predict(X_test_cv)
            fbeta = round(fbeta_score(y_test_cv,preds,beta=beta),4)
            
            if fbeta==0:
                pass
            else:
                fbeta_dict[str(weight)].append(fbeta)


# In[247]:


max_fbeta = 0
for key, values in fbeta_dict.items():
    fbeta = np.mean(values)
    if fbeta > max_fbeta:
        max_fbeta = fbeta
        max_weights = key
max_weights = ast.literal_eval(max_weights)
print("max_weights:",max_weights)
print("Mean max fbeta:",max_fbeta)


# In[248]:


logistic_regression = LogisticRegression(random_state=4, class_weight=max_weights)
logistic_regression.fit(X_train_lr, y_train);

test_scores_lr = logistic_regression.predict_proba(X_test_lr)[:,1]
test_pred_lr = logistic_regression.predict(X_test_lr)


# In[249]:


list(zip(X.columns,logistic_regression.coef_[0]))


# In[ ]:





# In[ ]:





# In[250]:


def create_confusion_matrix(y_test, test_pred, test_scores, title, filename):
    c_matrix = confusion_matrix(y_test, test_pred)
    plt.figure(dpi=80)
    sns.heatmap(c_matrix, cmap=plt.cm.Blues, annot=True, square=True, fmt='d',
    xticklabels=['Expansion', 'Recession'],
    yticklabels=['Expansion', 'Recession'])
    plt.title(title,weight="bold")
    plt.xlabel('prediction',weight="bold",labelpad=10)
    plt.ylabel('actual',weight="bold",labelpad=10)
    
    print(f"ROC AUC: {roc_auc_score(y_test, test_scores):.3f}")
    print(f"F_{beta:.3f} Score: {fbeta_score(y_test, test_pred, beta):.3f}")
    print(f"Precision: {precision_score(y_test, test_pred):.3f}")
    print(f"Recall: {recall_score(y_test, test_pred):.3f}")
    print(f"Accuracy: {accuracy_score(y_test, test_pred):.3f}")
    plt.savefig(path + filename + ".png", dpi=300)


# In[251]:


create_confusion_matrix(y_test, test_pred_lr, test_scores_lr, "Logistic Regression", "LR Confusion Matrix")


# In[ ]:





# In[ ]:





# In[252]:


def plot_ROC_curves(y_test, test_scores, title, filename):
    fpr, tpr, _ = roc_curve(y_test, test_scores)
    plt.plot(fpr, tpr, label=f"{title}")

    x = np.linspace(0,1,1000)
    plt.plot(x, x, linestyle='--')

    plt.title(f"{title} ROC Curve", weight="bold")
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    
    plt.savefig(path + filename + ".png", dpi=300)


# In[253]:


plot_ROC_curves(y_test, test_scores_lr, "Logistic Regression", "Logistic_Regression_ROC_AUC")


# In[254]:


def plot_results(df, column_name, file_name, title):
    fig, axs = plt.subplots(2,figsize=(10,12))
    for col in X.columns:
        if "SMA" in col:
            label = label=col[:-4]
        else:
            label = col
        axs[0].plot(df[col], "--", label=label)
        
    axs[0].xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    axs[0].set_ylabel("Feature values")
    axs[0].set_title(title, weight="bold")
    axs[0].axvline(train_split,color="r")
    
    ax1 = axs[0].twinx()
    ax1.plot(df["USREC"], "lightgray")
    ax1.fill_between(df.index,df["USREC"],color="lightgray",alpha=0.25)
    ax1.plot(df[column_name], "maroon", label="REC_SCORE")
    ax1.set_ylabel("Recession Score", labelpad=5)

    fig.legend(ncol=4, bbox_to_anchor=(0.82,-0.1), bbox_transform=ax1.transAxes, prop={"size": 10})
    plt.subplots_adjust(hspace=.3)
    
    # Plot S&P500
    axs[1].plot(df.index, (1+df["S&P500_total_return"]).rolling(12).apply(np.prod, raw=True)-1, label="S&P500")
    axs[1].set_ylabel("S&P500 rolling 12-month return")
    axs[1].set_title("Recessions (shaded) with S&P500 Overlay", weight="bold")
 
    ax2 = axs[1].twinx()
    ax2.plot(df["USREC"], "lightgray", label="USREC")
    ax2.fill_between(df.index,df["USREC"],color="lightgray",alpha=.25)
    ax2.axes.get_yaxis().set_ticks([])
    axs[1].axhline(y=0, color="r", linestyle="-")
    axs[1].xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    
    plt.savefig(path + file_name + ".png", dpi=300)


# In[255]:


df_SMA["LogReg_rec_score"] = logistic_regression.predict_proba(scaler.transform(X))[:,1]
plot_results(df_SMA, "LogReg_rec_score", "Logistic_Regression_Output", "Logistic Regression Scores")


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[256]:


stock_weight = 0.6
bond_weight = round(1-stock_weight,1)
asset_mix = str(int(stock_weight*100)) + ":" + str(int(bond_weight*100)) + "_return"
portfolio_weights = [{"stocks":x, "bonds":1-x} for x in np.arange(0.1,stock_weight + 0.1,0.1)]

risk_off_scores = np.arange(0.05,1.0,0.05)
risk_on_scores = np.arange(0.05,1.0,0.05)


# In[257]:


df_SMA["ttm_treasury_return"] = (1+(df_SMA["DGS10"].iloc[-12:].mean()/100))**(1/12)-1
df_SMA["60:40_return"] = 0.6 * df_SMA["S&P500_total_return"] + 0.4 * df_SMA["treasury_return"]
df_SMA["80:20_return"] = 0.8 * df_SMA["S&P500_total_return"] + 0.2 * df_SMA["treasury_return"]
df_SMA["100:0_return"] = df_SMA["S&P500_total_return"]

df_SMA["60:40_ttm_return"] = 0.6 * df_SMA["S&P500_total_return"] + 0.4 * df_SMA["ttm_treasury_return"]
df_SMA["80:20_ttm_return"] = 0.8 * df_SMA["S&P500_total_return"] + 0.2 * df_SMA["ttm_treasury_return"]


# In[258]:


allocation_fields = ["LogReg_rec_score","USREC","S&P500_total_return","treasury_return","ttm_treasury_return",
                     "60:40_return","60:40_ttm_return","80:20_return","80:20_ttm_return","100:0_return"]

allocation_train = df_SMA[df_SMA.index <= train_split][allocation_fields]
allocation_test = df_SMA[df_SMA.index > train_split][allocation_fields]


# In[ ]:





# In[ ]:





# In[259]:


allocation_train["stock_weight"] = stock_weight
allocation_train["bond_weight"] = bond_weight


# In[260]:


max_return = 0


for risk_off_score in risk_off_scores:
    
    risk_off_dates = allocation_train[(allocation_train["LogReg_rec_score"] >= risk_off_score) &
                   (allocation_train["LogReg_rec_score"] > allocation_train["LogReg_rec_score"].shift(12,fill_value=0))].index

    
    days_between = [risk_off_dates[i+1] - risk_off_dates[i] for i in range(len(risk_off_dates)-1)]
    dates_zipped = list(zip(days_between,risk_off_dates[1:]))
    
    
    try:
        risk_off_starts = [risk_off_dates[0]+relativedelta(months=+1)] + [element[1]+relativedelta(months=+1) 
                                                                      for element in dates_zipped 
                                                                      if element[0].days > 365]
    except:
        continue
    
   
    for risk_on_score in risk_on_scores:
        try:
            risk_on_starts = [allocation_train[(allocation_train["LogReg_rec_score"]<=risk_on_score) & 
                                               (allocation_train["LogReg_rec_score"]<allocation_train["LogReg_rec_score"].shift(12,fill_value=0)) &
                                               (allocation_train.index > start)].index[0]+relativedelta(months=+1) 
                              for start in risk_off_starts]
        except:
            continue
        
        allocation_shift_cycles = list(zip(risk_off_starts,risk_on_starts))

        for weight in portfolio_weights:
            
            allocation_train["trading_rule_returns"] = allocation_train[asset_mix]

            
            for cycle in allocation_shift_cycles:
                allocation_train["stock_weight"].loc[cycle[0]:cycle[1]] = weight["stocks"]
                allocation_train["bond_weight"].loc[cycle[0]:cycle[1]] = weight["bonds"]
                allocation_train["trading_rule_returns"].loc[cycle[0]:cycle[1]] =                allocation_train["stock_weight"] * allocation_train["S&P500_total_return"] +                allocation_train["bond_weight"] * allocation_train["treasury_return"]

            
            trading_return = np.prod(1 + allocation_train["trading_rule_returns"])
            if trading_return > max_return:
                max_return = trading_return
                allocation_train["optimal_stock_weight"] = allocation_train["stock_weight"]
                allocation_train["optimal_bond_weight"] = allocation_train["bond_weight"]
                allocation_train["optimal_returns"] = allocation_train["trading_rule_returns"]
                rule_params = {"risk off score": risk_off_score,"risk on score": risk_on_score,"weights": weight}
            
print(f"Max cumulative return: {max_return:0.3f}")
print(f"Rule parameters: {rule_params}")


# In[ ]:





# In[ ]:





# In[261]:


allocation_train.tail()


# In[ ]:





# In[262]:


def show_returns(df):
    years = (df.index.max() - df.index.min()).days/365
    print(f"CAGR for constant {asset_mix[0:5]} portfolio:",round((np.prod(1 + df[asset_mix])**(1/years)-1)*100,2),"%")
    
    print("CAGR for trading rule portfolio:",round((np.prod(1 + df["optimal_returns"])**(1/years)-1)*100,2),"%")
    print("")
    print(f"Std Dev for constant {asset_mix[0:5]} portfolio: {np.std(df[asset_mix])*100:0.3f}%")
    print(f"Std Dev for trading rule portfolio: {np.std(df['optimal_returns'])*100:0.3f}%")


# In[263]:


show_returns(allocation_train)


# In[ ]:





# In[ ]:





# In[ ]:





# In[264]:


def plot_weights(df, train_test):
    fig, ax = plt.subplots(figsize=(9,5))
    ax.plot(df["optimal_stock_weight"],"--",label="Stock weight")
    ax.plot(df["optimal_bond_weight"],"--",label="Bond weight")
    ax.plot(df["LogReg_rec_score"],label="Model Score")
    ax.legend(loc="best")
    ax.set_ylabel("Portfolio weights & Model score")
    ax.set_yticks(np.arange(0, 1, 0.1))
    plt.subplots_adjust(hspace=0.4)
    
    ax1 = ax.twinx()
    ax1.plot(df["USREC"],"lightgray",label="USREC")
    ax1.fill_between(df.index,df["USREC"],color="lightgray",alpha=0.25)
    ax1.get_yaxis().set_visible(False)
    ax.legend(ncol=3, bbox_to_anchor=(0.8,-0.08), bbox_transform=ax1.transAxes, prop={"size": 10})
    
    plt.savefig(path+asset_mix+"_"+train_test+".png", dpi=300);


# In[265]:


plot_weights(allocation_train, "train")


# In[ ]:





# In[ ]:





# In[ ]:





# In[266]:


def plot_returns(df, train_test, title):
    start_amt = 100000
    fig, ax = plt.subplots(figsize=(9,5))
    ax.plot(df.index,np.cumprod(1 + df["optimal_returns"])*start_amt, label="Trading Rule")
    ax.plot(np.cumprod(1 + df[asset_mix])*start_amt, label=asset_mix[0:5])
    ax.plot(np.cumprod(1 + df["treasury_return"])*start_amt, label="All Bonds")
    ax.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
    
    ax.legend(ncol=3, bbox_to_anchor=(0.78,-0.08), prop={"size": 10})
    ax.set_ylabel("Growth of $10,000")
    
    ax1 = ax.twinx()
    ax1.plot(df["USREC"], "lightgray", label="USREC")
    ax1.fill_between(df.index,df["USREC"],color="lightgray",alpha=0.25)
    ax1.get_yaxis().set_visible(False)
    
    plt.savefig(path + asset_mix[0:5] + "_" + train_test + ".png", dpi=300);


# In[267]:


plot_returns(allocation_train, "train", "")


# In[ ]:





# In[ ]:





# In[ ]:





# In[268]:


portfolio_weights = rule_params["weights"]
risk_off_score = rule_params["risk off score"]
risk_on_score = rule_params["risk on score"]

allocation_test["optimal_returns"] = allocation_test[asset_mix]
allocation_test["optimal_stock_weight"] = stock_weight
allocation_test["optimal_bond_weight"] = bond_weight

# Create list of dates where model score is greater than risk_off_score being tested
test_risk_off_dates = allocation_test[(allocation_test["LogReg_rec_score"] >= risk_off_score) &
                   (allocation_test["LogReg_rec_score"] > allocation_test["LogReg_rec_score"]
                    .shift(12,fill_value=0))].index

# If no dates are marked as risk off dates, exit code
if test_risk_off_dates.empty:
    pass
else:
    # Calculate days between each successive date and create zip object combining dates and those days between 
    test_days_between = [test_risk_off_dates[i+1]-test_risk_off_dates[i] for i in range(len(test_risk_off_dates)-1)]
    test_dates_zipped = list(zip(test_days_between,test_risk_off_dates[1:]))

    # Create list of the first days where the risk_off_score is hit. Separate different periods by one year
    test_risk_off_starts = [test_risk_off_dates[0]+relativedelta(months=+1)]+[element[1]+relativedelta(months=+1) 
                                                                                    for element in test_dates_zipped if element[0].days > 365]

    # Iterate through the risk_off_start dates and find a corresponding end date at which to get back into stocks
    test_risk_on_starts = [allocation_test[(allocation_test["LogReg_rec_score"] <= risk_on_score) 
                                      & (allocation_test["LogReg_rec_score"] < allocation_test["LogReg_rec_score"]
                                         .shift(12,fill_value=0)) 
                                      & (allocation_test.index > start)].index[0]+relativedelta(months=+1) for start in test_risk_off_starts]

    test_allocation_shift_cycles = list(zip(test_risk_off_starts, test_risk_on_starts))

    for cycle in test_allocation_shift_cycles:
        allocation_test["optimal_stock_weight"].loc[cycle[0]:cycle[1]] = portfolio_weights["stocks"]
        allocation_test["optimal_bond_weight"].loc[cycle[0]:cycle[1]] = portfolio_weights["bonds"]
        allocation_test["optimal_returns"].loc[cycle[0]:cycle[1]] =        allocation_test["optimal_stock_weight"] * allocation_test["S&P500_total_return"] +        allocation_test["optimal_bond_weight"] * allocation_test["treasury_return"]


# In[269]:


allocation_test.head()


# In[270]:


show_returns(allocation_test)


# In[271]:


plot_weights(allocation_test, "test")


# In[272]:


plot_returns(allocation_test, "test", "")


# In[273]:


print("Ending investment of trading rule portfolio:",int(np.prod(1+allocation_test["optimal_returns"])*100000))
print("Ending investment of passive portfolio:",int(np.prod(1+allocation_test[asset_mix])*100000))
print("Ending investment of 100% bond portfolio:",int(np.prod(1+allocation_test["treasury_return"])*100000))


# In[ ]:





# In[ ]:





# In[278]:


import tweepy
import logging
import os


# In[280]:


import os

folder_path = "C:/Users/Jeetesh/CAPSTONEEEE/CAPSTONE ALLOCATION/graphs"
file_names = os.listdir(folder_path)

for file_name in file_names:
    print(file_name)


# In[ ]:


import tweepy
import os

# Twitter API credentials
consumer_key = "your_consumer_key"
consumer_secret = "your_consumer_secret"
access_token = "your_access_token"
access_token_secret = "your_access_token_secret"

# Authenticate with Twitter API
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

# Get list of file names
folder_path = "C:/Users/Jeetesh/CAPSTONEEEE/CAPSTONE ALLOCATION/graphs"
file_names = os.listdir(folder_path)

# Create tweet
tweet_text = "Contents of {}:\n".format(folder_path)
for file_name in file_names:
    tweet_text += "- {}\n".format(file_name)

# Post tweet
api.update_status(tweet_text)


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[4]:


import os
import praw

# Replace CLIENT_ID, CLIENT_SECRET, USERNAME, and PASSWORD with your actual values
reddit = praw.Reddit(
    client_id='AafGycDGu3wQSscM8k8vSQ',
    client_secret='5z9OHaIOJy4-U0U4Oc8U-Ux5lZlXrQ',
    username='LuckyAir7055',
    password='mountaindew7',
    user_agent='MyApp/0.1 by LuckyAir7055'
)

# Set the subreddit where you want to post
subreddit = reddit.subreddit('r/recessionanalysis')

# Set the path to the folder containing the images
folder_path = 'C:/Users/Jeetesh/CAPSTONEEEE/CAPSTONE ALLOCATION/graphs'

# Loop through each file in the folder and submit it to Reddit
for file_name in os.listdir(folder_path):
    # Get the full path to the file
    file_path = os.path.join(folder_path, file_name)

    # Check if the file is an image file
    if file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
        try:
            # Submit the image to Reddit
            subreddit.submit_image(
                title=file_name,
                image_path=file_path,
                send_replies=False
            )
            print('Posted {} to Reddit'.format(file_name))
        except Exception as e:
            print('Failed to post {} to Reddit: {}'.format(file_name, e))


# In[ ]:




