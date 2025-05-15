#ifndef MISTAKE_H
#define MISTAKE_H

#include <string>
#include <vector>
using namespace std;

struct Mistake {
    string word;
    string time;  // 简化为字符串，如 "2025-05-14"
    int review_count;

    static void addMistake(int user_id, const string& word, const string& time);
    static vector<Mistake> loadMistakes(int user_id);
    static void showReviewPlan(int user_id);
};

#endif
