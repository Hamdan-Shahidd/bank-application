def my_function(*numbers):
    sum = 0
    for num in numbers:
        sum+=num
    return sum
print(my_function(2,4,5))