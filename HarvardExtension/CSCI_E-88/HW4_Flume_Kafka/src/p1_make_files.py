import os
# Create 5 files with 10 lines of text each (anything goes) - named file1.txt, file2.txt,.... File5.txt

output_folder = 'staging'

for i in range(1,6):
    with open('staging/file{}.txt'.format(i), 'w') as f:
        for j in range(1,11):
            f.write('I am line {} in file {}\n'.format(j, i))

print('\nDONE, contents of {}\n - {}'.format(output_folder, '\n - '.join(os.listdir(output_folder))))
