import csv

def loadResult():
  a = [0,0,0,0,0,0]
  with open('result.csv', 'r') as f:
    for row in csv.reader(f):
      a[int(row[1])-1] += 1
      if int(row[1]) == 6:
        print(row)

  print(f"turn: times")
  for i,v in enumerate(a):
    print(f"{i+1}: {v}")

  totalCount = sum(a)
  totalTurn = sum( (i+1)*v for i,v in enumerate(a))
  print(f"ave : {totalTurn/totalCount}")

loadResult()
