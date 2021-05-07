def bs(arr, v):

    l, r = 0, len(arr)
    while r - l > 0:
        i = (r + l) // 2
        if arr[i] < v:
            l = i+1
        elif arr[i] > v:
            r = i
        else:
            return i

    return l
