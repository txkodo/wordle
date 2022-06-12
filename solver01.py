from __future__ import annotations
import csv
from enum import Enum
import re
from typing import Tuple, TypeAlias
import math

class Word:
  @staticmethod
  def loadFromCsv(path:str):
    with open(path,encoding='utf8') as f:
      reader = csv.reader(f)
      return [Word(i[0],i[3],i[4]) for i in reader]

  @property
  def length(self) -> int:
    return len(self.spell)

  def __init__(self,spell:str,mean:str,desc:str) -> None:
    self.spell = spell.lower()
    self.mean = mean
    self.desc = desc

  def __str__(self):
    return f'{self.spell} {self.mean} {self.desc}'

  def match(self,regex:re.Pattern[str]) -> bool:
    return regex.match(self.spell) != None

class State(Enum):
  NOT = 0
  HAS = 1
  JUST = 2

n = State.NOT
h = State.HAS
j = State.JUST

Result :TypeAlias = Tuple[State,State,State,State,State]

def getResult(result:Result):
    return "".join(["⬛🟨🟩"[i.value] for i in result])

def resultToInt(result:Result):
    return sum( v.value *  3 ** i for i,v in enumerate(result))


class WordleWord:
  def __init__(self,spell:str) -> None:
    self.spell = spell
  
  def __str__(self):
    return self.spell

  def __eq__(self, other:object):
    if isinstance(other,WordleWord):
      return self.spell == other.spell
    return False
  
  # 他の単語と比較して結果を返す
  def check(self,pattern:WordleWord) -> Result:
    chars = [ i for i in self.spell]
    
    result = [State.NOT,State.NOT,State.NOT,State.NOT,State.NOT]
    
    passed = [False,False,False,False,False]

    # 同じ位置にあるかどうか
    for i, char in enumerate(pattern.spell):
      if self.spell[i] == char:
        result[i] = State.JUST
        chars.remove(char)
        passed[i] = True

    # 違う位置にあるかどうか
    for i, char in enumerate(pattern.spell):
      if passed[i]: continue
      if chars.count(char) != 0:
        result[i] = State.HAS
        chars.remove(char)

    return (
      result[0],
      result[1],
      result[2],
      result[3],
      result[4]
      )

class Wordle:
  def __init__(self,words:list[WordleWord],ans:WordleWord) -> None:
    self.words = words
    self.ans = ans

  def checkAll(self):
    for w in self.words:
      print(f"{w.spell}: {getResult(self.ans.check(w))}")

class WordleSolver:
  def __init__(self,words:list[WordleWord]) -> None:
    self.allWords = [ i for i in words]
    self.words = [w for w in words]
  
  def Filter(self,word:WordleWord,result:Result):
    self.words = [ w for w in self.words if w.check(word) == result]
  
  def solved(self):
    return len(self.words) == 1

  def FindBest(self):
    def getHensa(word:WordleWord) -> float:
      total = 3 ** 5
      counts = [0] * total
      for w in self.words:
        r = word.check(w)
        counts[resultToInt(r)] += 1
      
      ave = sum(counts) / total
      return (sum( (ave - count) ** 2  for count in counts ) / total)**0.5
    
    min = math.inf
    minIndex = -1

    for i,w in enumerate(self.allWords):
      h = getHensa(w)
      ignore = 0.000000000000001

      if h < (min - ignore) or ( (h - min) < ignore and any( i.spell == w.spell for i in self.words )):
        min = h
        minIndex = i
    
    return self.allWords[minIndex]

  def FindWorst(self):
    def getHensa(word:WordleWord) -> float:
      total = 3 ** 5
      counts = [0] * total
      for w in self.words:
        r = word.check(w)
        counts[resultToInt(r)] += 1
      
      ave = sum(counts) / total
      return (sum( (ave - count) ** 2  for count in counts ) / total)**0.5
    
    min = math.inf
    minIndex = -1

    for i,w in enumerate(self.allWords):
      h = getHensa(w)
      ignore = 0.000000000000001

      if h > (min + ignore) or ( (h - min) < ignore and any( i.spell == w.spell for i in self.words )):
        min = h
        minIndex = i
    
    return self.allWords[minIndex]

  def printAll(self):
    for w in self.words:
      print(w)

  def printCount(self):
    l = len(self.words)
    print("count: {l}")
    if (l < 30):
      print("====== words ======")
      self.printAll()

  def formattedPrint(self):
      l = len(self.words)

      if (l < 30):
        print("====== words ======")
        self.printAll()
        print("====== words ======")

      print(f"count: {l}")
      print(f"best:  {self.FindBest()}")

path = r"wordle-answers-alphabetical.txt"
with open(path,encoding='utf8') as f:
  reader = csv.reader(f)
  words = [WordleWord(i[0]) for i in reader]

s = WordleSolver(words)
s.Filter(WordleWord("trode"),(j,j,j,n,j))
# s.Filter(WordleWord("prong"),(n,j,j,n,n))
# s.Filter(WordleWord("beast"),(n,h,n,n,h))
# s.Filter(WordleWord("wrote"),(n,j,j,h,j))
# s.Filter(WordleWord("froze"),(n,n,h,n,n))

choice = s.FindBest()
s.formattedPrint()
# print(s.FindWorst())
