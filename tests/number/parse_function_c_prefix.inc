bool int_double(int64_t in, int32_t* out, const char** error){
    if (in == 13){
        *error = "unlucky";
        return true;
    }
    *out = (int32_t) (in * 2);
    return false;
}
