#generate a file with 100 lines:
#each line should have 3 random numbers in the range [0-10]
#your lines would look like:
#"1 7 3"
#" 2 1 3"

from random import randint

nums = []
for i in range(100):
    line = ' '.join(str(randint(0, 10)) for j in range(3))
    nums.append('{0}\n'.format(line))

#orig windows path: with open('c:/temp/assign00_output.txt, 'w') as f:
with open('/tmp/assign00_output.txt', 'w') as f:
        f.writelines(nums)

