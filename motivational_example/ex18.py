def adjust_buildings_bonus(students_A, admins_A, students_B, admins_B, profs_B):
   
    total_A = sum(students_A) + sum(admins_A)
    total_B = sum(students_B) + sum(admins_B) +sum(profs_B)
    
    surplus = abs(total_A - total_B)
    
    stayers = total_A + total_B - surplus
    bonus_pool = stayers * 10
   
    bonus_per_moved = bonus_pool / surplus
    
    return  bonus_per_moved


#read from user the 5 lists
# the user must provide the input in th forma1
students_A = list(map(int, input().split()))
admins_A = list(map(int, input().split()))
students_B = list(map(int, input().split()))
admins_B = list(map(int, input().split()))
profs_B = list(map(int, input().split()))
print(adjust_buildings_bonus(students_A, admins_A, students_B, admins_B, profs_B))