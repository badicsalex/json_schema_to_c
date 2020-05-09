extern char last_error[10000];
extern int last_error_pos;

void check_error(const char* json, const char* expected_str, int expected_pos);
