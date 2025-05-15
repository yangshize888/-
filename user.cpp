// User.cpp
#include "user.h"
#include <fstream>
#include <sstream>
#include <iostream>

std::map<std::string, std::pair<std::string, int>> User::userTable;
std::string User::userFile = "users.txt";

bool User::loadUserTable() {
    userTable.clear();
    std::ifstream infile(userFile);
    if (!infile) return false;

    std::string line;
    while (getline(infile, line)) {
        std::istringstream iss(line);
        std::string username, password;
        int id;
        if (iss >> username >> password >> id) {
            userTable[username] = {password, id};
        }
    }
    return true;
}

bool User::saveUserTable() {
    std::ofstream outfile(userFile);
    if (!outfile) return false;
    for (const auto& pair : userTable) {
        outfile << pair.first << " " << pair.second.first << " " << pair.second.second << "\n";
    }
    return true;
}

bool User::registerUser(const std::string& username, const std::string& password) {
    if (userTable.find(username) != userTable.end()) {
        std::cout << "用户名已被注册！\n";
        return false;
    }
    loadUserTable();
    int newId = userTable.size() + 1;
    userTable[username] = {password, newId};
    saveUserTable();
    std::ofstream dataFile(getUserDataFile(newId)); // 创建该用户的词库文件
    dataFile.close();
    std::cout << "注册成功，用户ID: " << newId << "\n";
    return true;
}

int User::loginUser(const std::string& username, const std::string& password) {
    loadUserTable();
    if (userTable.find(username) != userTable.end()) {
        if (userTable[username].first == password) {
            return userTable[username].second;
        }
    }
    return -1;
}

std::string User::getUserDataFile(int userId) {
    return "user_" + std::to_string(userId) + "_words.txt";
}
