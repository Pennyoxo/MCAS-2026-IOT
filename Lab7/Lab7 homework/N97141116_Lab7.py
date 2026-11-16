import numpy as np 
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

data = np.loadtxt("Bank_Customer.csv",skiprows=1,dtype=str,delimiter=',')

'''
Your work
非數值型資料需轉換成數值型資料 (country, gender)
去除掉無意義的特徵類別 (customer_id)
標準化特徵 (StandardScaler)
'''

# (1) 純數值欄位：credit_score, age, tenure, balance,
#     products_number, credit_card, active_member, estimated_salary
num = data[:, [1, 4, 5, 6, 7, 8, 9, 10]].astype(float)

# (2) gender → Male=1, Female=0
gender = np.where(data[:, 3] == "Male", 1, 0)

# (3) country → one-hot（拆成三欄）
france  = (data[:, 2] == "France").astype(float)
germany = (data[:, 2] == "Germany").astype(float)
spain   = (data[:, 2] == "Spain").astype(float)

# (4) 把所有特徵並排成 X
X = np.column_stack([num, gender, france, germany, spain])

# (5) 標準化特徵（平均 0、標準差 1）
scaler = StandardScaler()
X = scaler.fit_transform(X)

# (6) 答案 y = churn
y = data[:, 11].astype(float)

# 特徵 + 答案合併，最後一欄是 churn
pre_data = np.column_stack([X, y])


np.savetxt("Bank_Customer_Preprocessed.csv", pre_data, delimiter=",")


from sklearn.linear_model import LogisticRegression 
# 決策分類器
clf = LogisticRegression()

'''
Your work
切割 data 為 x_train, x_test, y_train, y_test
請學習 train_test_split 的使用方法
'''
# 從前處理好的資料拿出特徵 x（前 12 欄）和答案 y（最後一欄）
x = pre_data[:, :-1]
y = pre_data[:, -1]

# 70% 當訓練資料、30% 當測試資料
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=42)

# 使用訓練集來訓練我們的分類器
clf.fit(x_train, y_train)
# 測試資料集中進行預測
pred = clf.predict(x_test)

#print (pred) # 預測分類，即客戶是否流失
#print (y_test) # 分類
print (str(accuracy_score(pred, y_test)*100 ) + "% ")   # 預測精度 