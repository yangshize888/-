// User.h
#ifndef USER_H
#define USER_H

#include <string>
#include <map>

class User {
public:
    static bool registerUser(const std::string& username, const std::string& password);
    static int loginUser(const std::string& username, const std::string& password);
    static std::string getUserDataFile(int userId); // 每个用户的专属文件路径
private:
    static std::map<std::string, std::pair<std::string, int>> userTable;
    static bool loadUserTable();
    static bool saveUserTable();
    static std::string userFile;
};

#endif
