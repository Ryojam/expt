#include <bits/stdc++.h>
using namespace std;


//Step #1. 変数を宣言
int N;                     //商品の個数
int L;                     //値段合計の上限
string menu[109];          // menu[i]: 商品iのカロリー
long long V[109],W[109];   //V[i]: 商品iのカロリー, W[i]:商品iの値段
long long dp[109][100009]; //dp[i][j]: 商品iを選ぶとき、値段の合計j円の場合のカロリー

//メインプログラム
int main(){
//  Step #2. 標準入力
    cout << "商品の個数を入力" << endl;
    cin >> N;
    cout << "上限の値段を入力" << endl;
    cin >> L;
    for(int i=1;i<=N;i++){
        cin >> menu[i] >>V[i] >> W[i];
    }

//  Step #3. 動的計画法
    dp[0][0] = 0;
    for(int i=1;i<=N;i++){
        for(int j=0;j<=L;j++){
            if(j < W[i]) dp[i][j] = dp[i-1][j];
            else dp[i][j] = max(dp[i-1][j],dp[i-1][j-W[i]]+V[i]);
        }
    }
    
    int answer = dp[N][L]; //最大カロリー

//  Step #4. 動的計画法の復元
    int x = L;
    vector<int> ret;
    for (int i = N; i >= 1; i--) {
        if (dp[i][x] == dp[i - 1][x]) {// 商品 x を選ばない
        }
        else {// 商品 x を選ぶ
            ret.push_back(i);
            x -= W[i];
            
        }
    }
    reverse(ret.begin(), ret.end());
    
//  Step #5. 合計金額の計算
    int mxW_sum = 0;
    for(int i=0;i<ret.size();i++){
        mxW_sum += W[ret[i]];
    }

//  Step #6. 出力
    cout << "menu:" << endl;
    for(int i=0;i<ret.size();i++){
        cout << "     " << "menu" << ret[i];
        if(ret[i] < 10) cout<< "   " << menu[ret[i]] << "  " << V[ret[i]] << "kcal" << "  " << "¥" << W[ret[i]]  << endl;
        else cout<< "  " << menu[ret[i]] << "  " << V[ret[i]] << "kcal" << "  " << "¥"<< W[ret[i]]  << endl;
        }
    cout << endl;
    cout <<"Total:  " << ret.size() << " item" << "  "<< answer <<"kcal"<< "  " << "¥" << mxW_sum <<  endl;

    return 0;
}
