

from math import ceil, log


def intListToByte(l:list[list[int]],max:int):
  result = b''
  order = ceil(log(max,256))
  height = len(l)
  width = len(l[0])

  result += order.to_bytes(1,'big')
  result += height.to_bytes(2,'big')
  result += width.to_bytes(2,'big')
  for r in l:
    for v in r:
      result += v.to_bytes(order,'big')
  return result

def byteToIntList(b:bytes):
  order =  b[0]
  height = int.from_bytes(b[1:3],'big')
  width = int.from_bytes(b[3:5],'big')
  index = 5
  result:list[list[int]] = []
  for _ in range(height):
    res:list[int] = []
    for _ in range(width):
      res.append(int.from_bytes(b[index:(index+order)],'big'))
      index += order
    result.append(res)
  return result

def saveDat(l:list[list[int]]):
  with open(f'test.dat', 'bw') as f:
    f.write(intListToByte(l,100))

def loadDat() -> list[list[int]]:
  with open(f'test.dat', 'br') as f:
    a = byteToIntList(f.read())
  return a

v = [[1,2,3,4],[1,2,3,4],[3,4,5,6]]

saveDat(v)

print(loadDat())
