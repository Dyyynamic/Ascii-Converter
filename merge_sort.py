def print_chars(left, right, size):
  print((left*size + right*size + '\n') * int(size/2))

def merge_sort(arr):
  if len(arr) > 1:
    mid = len(arr) // 2

    L = arr[:mid]
    R = arr[mid:]

    merge_sort(L)
    merge_sort(R)

    i = j = k = 0

    # Copy data to temp arrays L[] and R[]
    while i < len(L) and j < len(R):
      choice = None
      while choice not in ('l', 'r'):
        print_chars(L[i], R[j], 50)
        choice = input('l or r? ')
      
      if choice == 'l':
        arr[k] = L[i]
        i += 1
      else:
        arr[k] = R[j]
        j += 1
      k += 1

    # Checking if any element was left
    while i < len(L):
      arr[k] = L[i]
      i += 1
      k += 1

    while j < len(R):
      arr[k] = R[j]
      j += 1
      k += 1

if __name__ == '__main__':
  chars = list('$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,"^`\'. ')
  
  print("Given array is")
  print(''.join(chars))
  
  merge_sort(chars)
  
  print("\nSorted array is ")
  print(''.join(chars))
