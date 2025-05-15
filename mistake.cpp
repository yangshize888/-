#include "mistake.h"
#include <fstream>
#include <iostream>
#include <sstream>

void Mistake::addMistake(int user_id, const string& word, const string& time) {
    string filename = "data/mistakes_" + to_string(user_id) + ".txt";
    ofstream out(filename, ios::app);
    out << word << "," << time << ",0\n";
}

vector<Mistake> Mistake::loadMistakes(int user_id) {
    vector<Mistake> mistakes;
    string filename = "data/mistakes_" + to_string(user_id) + ".txt";
    ifstream in(filename);
    string line;
    while (getline(in, line)) {
        istringstream iss(line);
        string word, time, count_str;
        getline(iss, word, ',');
        getline(iss, time, ',');
        getline(iss, count_str, ',');

        Mistake m = { word, time, stoi(count_str) };
        mistakes.push_back(m);
    }
    return mistakes;
}

void Mistake::showReviewPlan(int user_id) {
    auto mistakes = loadMistakes(user_id);
    cout << "===== review plan =====\n";
    for (const auto& m : mistakes) {
        if (m.review_count < 5) { // 简化计划：复习5次
            cout << "word:" << m.word << ", need review" << (5 - m.review_count) << " times\n";
        }
    }
}
