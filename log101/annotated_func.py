#State of the program right berfore the function call: l and r are integers such that 1 <= l <= r < 10^18, and k is an integer such that 1 <= k <= 10.
def func():
    t, s, x = map(int, input().split())
    if ((x - t) % s == 0 or (x - t) % s == 1) :
        print('YES')
    else :
        print('NO')
    #State of the program after the if-else block has been executed: *`l` and `r` are integers such that 1 <= `l` <= `r` < 10^18, `k` is an integer such that 1 <= `k` <= 10; `t`, `s`, `x` are input integers. If the current value of `(x - t) % s` is either 0 or 1, the program prints 'YES'. Otherwise, if `(x - t) % s` is not equal to 0 and not equal to 1, the program prints 'NO'.
#Overall this is what the function does:The function accepts three integers `t`, `s`, and `x` from user input. It checks if the difference between `x` and `t` is either divisible by `s` or leaves a remainder of 1 when divided by `s`. If either condition is true, it prints 'YES'; otherwise, it prints 'NO'. The function does not take parameters `l`, `r`, or `k` as described in the annotations, and it does not return any value.

