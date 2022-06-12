from itertools import repeat
from urllib.request import urlopen
import numpy
from multiprocessing import Pool,Value, Array
from tqdm import tqdm

def getWordList() -> list[bytes]:
  with urlopen('https://gist.githubusercontent.com/cfreshman/a03ef2cba789d8cf00c08f767e0fad7b/raw/5d752e5f0702da315298a6bb5a771586d6ff445c/wordle-answers-alphabetical.txt') as response:
    text:bytes = response.read()
  return text.split()

def resultToStr(result:int):
  r = ""
  for _ in range(5):
    r += "⬛🟨🟩"[result % 3]
    result //= 3
  return r

# def quickCheck(ans:int,choise:int):
#   return checked[ans,choise]

class WordleSolver:
  def __init__(self,resultmap:list[set[int]],count:int) -> None:
    self.resultmap = resultmap
    self.count = count
    self.words = set(range(count))
    self._best = None
  
  @property
  def length(self):
    return len(self.words)
    
  @property
  def best(self) -> int:
    if self._best is None:
      return self.findBest()
    return self._best
  
  def filter(self,word:int,result:int):
    self.words.intersection_update(self.resultmap[word*243 + result])
    self._best = None
  
  def findBest(self):
    vals = numpy.zeros(243,dtype=numpy.intp)
    stds:numpy.ndarray = numpy.zeros(self.count)

    for i in range(self.count):
      for j in range(243):
        # print(j,self.resultmap.__len__(),self.count*i+j)
        vals[j] = len(self.resultmap[243*i+j].intersection(self.words))
      stds[i] = numpy.std(vals)
    minIndex = stds.argmin()
    best = minIndex
    self._best = best
    return best
  
  # def print(self):
  #   if self.length < 20:
  #     print(f"words:{'/'.join(map(lambda x: words[x].decode('utf-8'), self.words))}")
  #   print(f"count:{self.length}")
  #   print(f"best :{self.best}")

def solve(arg : tuple[list[set[int]],int,int,list[bytes]]):
  resultmap,count,answer,words = arg
  def check(ans:int,choise:int) -> int:
    a:list[bytes] = list(words[ans])
    c = words[choise]
    # 0 含まれていない
    # 1 位置は違う
    # 2 位置まで一致
    result = [0,0,0,0,0]
    for i in range(5):
      if a[i] == c[i]:
        result[i] = 2
        a[i] = b' '
    for i in range(5):
      if a[i] != ' ':
        try:
          j = a.index(c[i])
          result[i] = 1
          a[j] = b' '
        except ValueError:
          continue
    r = ( result[0] + result[1] * 3 + result[2] * 9 + result[3] * 27 + result[4] * 81 )
    return r

  s = WordleSolver(resultmap,count)
  # aroseのインデックス
  choice = 108
  turn = 1
  # choices:list[bytes] = []
  while s.length != 1:
    s.filter(choice,check(answer,choice))
    choice = s.best
    turn += 1
  return turn

def main():
  words = getWordList()
  count = len(words)

  def check(ans:int,choise:int) -> int:
    a:list[bytes] = list(words[ans])
    c = words[choise]
    # 0 含まれていない
    # 1 位置は違う
    # 2 位置まで一致
    result = [0,0,0,0,0]
    for i in range(5):
      if a[i] == c[i]:
        result[i] = 2
        a[i] = b' '
    for i in range(5):
      if a[i] != ' ':
        try:
          j = a.index(c[i])
          result[i] = 1
          a[j] = b' '
        except ValueError:
          continue
    r = ( result[0] + result[1] * 3 + result[2] * 9 + result[3] * 27 + result[4] * 81 )
    return r

  resultmap:list[set[int]] = [set() for _ in range(count * 3**5)]
  def g(i:int,j:int):
    resultmap[j*243+check(i,j)].add(i)
  [g(i,j) for i in range(count) for j in range(count)]

  with Pool() as pool:
    results:list[int] = list(tqdm(pool.imap(solve,zip(repeat(resultmap),repeat(count),range(count),repeat(words))),total=count))


  # def solve(answer:int):
  #   def check(ans:int,choise:int) -> int:
  #     a:list[bytes] = list(words[ans])
  #     c = words[choise]
  #     # 0 含まれていない
  #     # 1 位置は違う
  #     # 2 位置まで一致
  #     result = [0,0,0,0,0]
  #     for i in range(5):
  #       if a[i] == c[i]:
  #         result[i] = 2
  #         a[i] = b' '
  #     for i in range(5):
  #       if a[i] != ' ':
  #         try:
  #           j = a.index(c[i])
  #           result[i] = 1
  #           a[j] = b' '
  #         except ValueError:
  #           continue
  #     r = ( result[0] + result[1] * 3 + result[2] * 9 + result[3] * 27 + result[4] * 81 )
  #     return r

  #   s = WordleSolver(resultmap,count)
  #   # aroseのインデックス
  #   choice = 108
  #   turn = 1
  #   # choices:list[bytes] = []
  #   while s.length != 1:
  #     s.filter(choice,check(answer,choice))
  #     choice = s.best
  #     turn += 1
  #   return turn

  # results:list[int] = []
  # for i in range(count):
  #   print(i)
  #   solve(i)
  #   print(i)

  
  for i in range(1,7):
    print(f"{i}: {results.count(i)}")
  print(f"ave: {sum(results)/count}")

if __name__ == "__main__":
  main()
