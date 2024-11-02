#include <random>
#include <chrono>
#include <thread>
#include <bits/stdc++.h>
using namespace std;

int get_rand_range(int min_val, int max_val) {
    // 乱数生成器
    random_device rd;
    static mt19937 mt(rd());

    // [min_val, max_val] の一様分布整数 (int) の分布生成器
    uniform_int_distribution<int> get_rand_uni_int(min_val, max_val);

    // 乱数を生成
    return get_rand_uni_int(mt);
}

int kuji(int N,int *xme,int xsi){
    int size=100001;
    int list[size];
    int num[size];
    int Mx = 50000*(N-1);
    for(int i=1;i<=size;i++){
        num[i] = get_rand_range(0,Mx);
        int m = 1;
        while(num[i] > 0){
            m++;
            num[i]-=50000;
      
        }
        list[i]= m;
    
    }
    int ans = list[get_rand_range(1,size)];
    bool ch = false;
    while(ch == false){
        int check = 0;
        for(int i=1;i<=xsi;i++){
            if(xme[i] == ans){
                ans = list[get_rand_range(1,size)];
            }
                
            else{
                check++;
            }
        }
        if(check == xsi){
            ch = true;
        }
    }

  return ans;

}

int main(){
    int N;
    cout << "人数を入力" << " ";
    cin >> N;
    cout <<endl <<"除く人数を入力" << " ";
    int xsi;
    cin >> xsi;
    cout <<endl <<"除く人の番号を入力" << " ";
    int xme[100];
    for(int i=1;i<=100;i++){  
        xme[i] = -1;
    }
  
    for(int i=1;i<=xsi;i++){
        cin >> xme[i];
    }
  
    int num=kuji(N, xme,xsi);
    cout <<endl << endl << "#############################" << endl << endl;
    this_thread::sleep_for(std::chrono::milliseconds(1000));
    cout << endl << " " << "5" << endl << endl;
    this_thread::sleep_for(std::chrono::milliseconds(1000));
    cout << endl << " " << "4" << endl << endl;
    this_thread::sleep_for(std::chrono::milliseconds(1000));
    cout << endl << " " << "3" << endl << endl;
    this_thread::sleep_for(std::chrono::milliseconds(1000));
    cout << endl << " " << "2" << endl << endl;
    this_thread::sleep_for(std::chrono::milliseconds(1000));
    cout << endl << " " << "1" << endl << endl;
    this_thread::sleep_for(std::chrono::milliseconds(1000));
  
    cout <<endl << endl << "#############################" << endl << endl << endl;
    cout << " " << "A selected number is ..." << " ";
    this_thread::sleep_for(std::chrono::milliseconds(500));
    printf("\x1b[31m%d",num);	
    printf("\x1b[39m\n");
  
    cout <<endl  << endl <<  "#############################" << endl << endl << endl;
    this_thread::sleep_for(std::chrono::milliseconds(3000));
    printf("\x1b[32m...Program was complete.\n");
  
    return 0;

}
