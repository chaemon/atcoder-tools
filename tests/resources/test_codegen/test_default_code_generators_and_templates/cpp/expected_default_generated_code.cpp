#include<iostream>
#include<vector>
#include<string>

const long long MOD = 123;
const std::string YES = "yes";
const std::string NO = "NO";

void solve(long long N, long long M, std::vector<std::vector<std::string>> H, std::vector<long long> A, std::vector<long double> B, long long Q, std::vector<long long> X){

}

// Generated by x.y.z https://github.com/kyuridenamida/atcoder-tools  (tips: You use the default template now. You can remove this line by using your custom template)
int main(){
    long long N;
    std::cin >> N;
    long long M;
    std::cin >> M;
    std::vector<std::vector<std::string>> H(N-2+1, std::vector<std::string>(M-1-2+1));
    for(int i = 0 ; i < N-2+1 ; i++){
        for(int j = 0 ; j < M-1-2+1 ; j++){
            std::cin >> H[i][j];
        }
    }
    std::vector<long long> A(N-2+1);
    std::vector<long double> B(N-2+1);
    for(int i = 0 ; i < N-2+1 ; i++){
        std::cin >> A[i];
        std::cin >> B[i];
    }
    long long Q;
    std::cin >> Q;
    std::vector<long long> X(M+Q);
    for(int i = 0 ; i < M+Q ; i++){
        std::cin >> X[i];
    }
    solve(N, M, std::move(H), std::move(A), std::move(B), Q, std::move(X));
    return 0;
}
