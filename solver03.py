from itertools import cycle, product, repeat
from unicodedata import name
from urllib.request import urlopen
import numpy as np

def getWordList() -> list[str]:
  with urlopen('https://gist.githubusercontent.com/cfreshman/a03ef2cba789d8cf00c08f767e0fad7b/raw/5d752e5f0702da315298a6bb5a771586d6ff445c/wordle-answers-alphabetical.txt') as response:
    text:bytes = response.read()
  return list(map( lambda x:x.decode(encoding='utf-8') , text.split()))

def resultToStr(result:int):
  r = ""
  for _ in range(5):
    r += "⬛🟨🟩"[result % 3]
    result //= 3
  return r

class WordleWords:
  def __init__(self,words:list[str]) -> None:
    self.words = words
    self.length = len(words)

    range = np.arange(0,self.length)
    uCheck = np.frompyfunc(self._check, 2, 1)
    self.checkMap = uCheck.outer(range,range)
  
  def check(self,ans:int,choise:int) -> int:
    return self.checkMap[ans][choise]

  def _check(self,ans:int,choise:int) -> int:
    a:list[str] = list(self.words[ans])
    c = self.words[choise]
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

class WordleSolver:
  def __init__(self,words:WordleWords) -> None:
    self.words = words
    self.answers = list(range(words.length))
    self.states = np.zeros((words.length,243))
    self._best = None
    self.choise = None

  def length(self):
    return len(self.answers)
    
  def filter(self,choice:int,result:int):
    self._best = None
    self.choise = choice
    self.answers = [ ans for ans in self.answers if self.words.check(ans,choice) == result ]
  
  def best(self) -> int:
    if self._best:
      return self._best
    return self._findbest()

  def _findbest(self) -> int:
    if len(self.answers) == 1:
      return self.answers[0]
    self.states.fill(0)
    
    for ans,choice in product(self.answers,range(self.words.length)):
      self.states[choice][self.words.check(ans,choice)] += 1

    m = np.std(self.states,1).argmin()
    self._best = m
    return m

  def formattedPrint(self):
      l = len(self.answers)
      if (l < 30):
        print(f"words: {'/'.join(map(lambda x: self.words.words[x],self.answers))}")
      print(f"count: {l}")
      if self.choise:
        print(f"choice: {self.words.words[self.choise]}")
      print(f"best:  {self.words.words[self.best()]}")

def solve(solver:WordleSolver,word:int):
  # aroseのインデックス
  choice = 108
  p = solver.words.words[choice]
  turn = 1
  while choice != word:
    result = solver.words.check(word,choice)
    solver.filter(choice,result)
    choice = solver.best()
    p += f" > {solver.words.words[choice]}"
    turn += 1
    if turn >= 5:
      print(p)
  print(f"{solver.words.words[word]} [{turn}] {p}")
  return turn

def solveMulti(arg:tuple[WordleSolver,int]):
  solve(*arg)
words =getWordList()
a = WordleWords(words)
solver = WordleSolver(a)

from multiprocessing import Pool
from tqdm import tqdm
if __name__ == "__main__":  

  with Pool() as p:
    p.map(solveMulti,zip(repeat(solver),range(len(words))))
  