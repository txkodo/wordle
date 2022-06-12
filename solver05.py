import csv
from itertools import repeat
from math import ceil, log, log2
from multiprocessing import Pool
from pathlib import Path
import numpy as np
from tqdm import tqdm
from console import Color, Console
import re

LETTER = 11

def getAnswers() -> list[str]:
  return Path(f"{LETTER}answer.txt").read_text().split()

def getGuesses() -> list[str]:
  return Path(f"{LETTER}guess.txt").read_text().split()

def resultToStr(result:int):
  r = ""
  for _ in range(LETTER):
    r += "⬛🟨🟩"[result % 3]
    result //= 3
  return r

def check(ans:str,choice:str) -> int:
  a:list[str] = list(ans)
  # 0 含まれていない
  # 1 位置は違う
  # 2 位置まで一致
  result = [0] * LETTER
  for i in range(LETTER):
    if a[i] == choice[i]:
      result[i] = 2
      a[i] = '*'
  for i in range(LETTER):
    if a[i] != '*':
      try:
        j = a.index(choice[i])
        result[i] = 1
        a[j] = '#'
      except ValueError:
        continue
  r = sum( 3**i * v for i,v in enumerate(result) )
  return r

def checkMulti(arg:tuple[str,list[str]]):
  return [check(j,arg[0]) for j in arg[1]]

# def intListToByte(l:list[list[int]],max:int):
#   result = b''
#   order = ceil(log(max,256))
#   height = len(l)
#   width = len(l[0])

#   result += order.to_bytes(1,'big')
#   result += height.to_bytes(2,'big')
#   result += width.to_bytes(2,'big')
#   for r in l:
#     for v in r:
#       result += v.to_bytes(order,'big')
#   return result

# def byteToIntList(b:bytes):
#   order =  b[0]
#   height = int.from_bytes(b[1:3],'big')
#   width = int.from_bytes(b[3:5],'big')
#   index = 5


#   result:list[list[int]] = []
#   for _ in range(height):
#     res:list[int] = []
#     for _ in range(width):
#       res.append(int.from_bytes(b[index:(index+order)],'big'))
#       index += order
#     result.append(res)
#   return result

def saveDat():
  ans = getAnswers()
  guess = getGuesses()
  with open(f'pattern{LETTER}', 'bw') as f:
    with Pool() as p:
      np.save(f,np.array(list(tqdm(p.imap(checkMulti,zip(ans + guess,repeat(ans))),total=len(ans + guess)))))

answerCount = 0
totalCount = 0

def loadDat() -> list[list[int]]:
  print("start load pattern data")
  global answerCount
  global totalCount
  with open(f'pattern{LETTER}', 'br') as f:
    l:list[list[int]] = np.load(f)
    answerCount = len(l)
    totalCount = len(l[0])
  print("end load pattern data")
  return l
  
ans = getAnswers()
guess = getGuesses()
total = guess + ans

pattern = [[ int(j) for j in i ] for i in loadDat()]

class WordleSolver:
  def __init__(self,pattern:list[list[int]]) -> None:
    self.pattern = pattern
    self.answers = set(range(answerCount))
    self.guesses = range(totalCount)
    self.choise = None
    self._best = None
  
  @property
  def best(self) -> int:
    if self._best:
      return self._best
    return self.getBestWord()
  
  def filter(self,choice:str,result:str):
    c = total.index(choice)
    r = sum( "nhj".index(v) * 3 ** i for i,v in enumerate(result))
    self.filterInt(c,r)

  def filterInt(self,choice:int,result:int):
    self._best = None
    self.choise = choice
    self.answers = { ans for ans in self.answers if self.pattern[choice][ans] == result }
  
  def getWordPotential(self,word:int) -> float:
    patterns = [0] * 3 ** LETTER
    w = self.pattern[word]
    for i in self.answers:
      patterns[w[i]] += 1
    
    p = [ patterns[i] / totalCount for i in range(3 ** LETTER) ]
    potential = sum( 0 if i == 0 else i * log2(1/i) for i in p )

    return potential
  
  def getBestWord(self) -> int:
    if len(self.answers) == 1:
      self._best = self.answers.pop()
      return self._best
    word = 0
    max = 0
    for guess in self.guesses:
      w = self.getWordPotential(guess)
      if w > max or ( w == max and guess in self.answers ):
        word = guess
        max = w
    self._best = word
    return word

  def formattedPrint(self):
      l = len(self.answers)
      if (l < 30):
        print(f"words: {'/'.join(map(lambda x: ans[x],self.answers))}")
      print(f"count: {l}")
      if self.choise is not None:
        print(f"choice: {total[self.choise]}")
      print(f"best:  {total[self.best]}")

BEST = total[WordleSolver(pattern).best]

def dialogue():
  solver = WordleSolver(pattern)

  best = BEST
  turn = 1

  console = Console()

  results = console.addLine()
  results.addText("== Wordle ==")
  console.addLine().addText("============")

  bestLine = console.addLine()
  bestLine.addText("best: ")
  bestText = bestLine.addText(best)

  answersLine = console.addLine()
  answersLine.addText("answers: ")
  answerCountText = answersLine.addText()
  answerCountText.bold = True
  answerValuesText = answersLine.addText()

  bestText.bold = True

  while len(solver.answers) > 1:
    console.reWrite()
    word = console.getInput(
      "...input word what did you choosed or nothing ( when you choosed best word )",
      lambda w:f"...input word what did you choosed ('{w}' is not available)",
      lambda w: (w == "" or w in total)
    ) or best
    results.addText(f"\n{turn}: ")
    resultChars = [results.addText(word[i]) for i in range(LETTER)]
    console.reWrite()

    result = console.getInput(
      "...input result e.g. 'nhjnh'",
      lambda w:f"...input result e.g. 'nhjnh' ('{w}' is not valid)",
      lambda w: re.fullmatch(f"[nhj]{{{LETTER}}}",w) != None
    )

    colorMap = {
      'n': Color.WHITE,
      'h': Color.YELLOW,
      'j': Color.GREEN
    }
    for char,state in zip(resultChars,result):
      char.bold = True
      char.color = colorMap[state]
    
    if result == "j" * LETTER:
      bestLine.delete()
      answersLine.delete()
      console.addLine().addText("solved !!")
      answerLine = console.addLine()
      answerLine.addText("answer: ")
      a = answerLine.addText(word)
      a.bold = True
      a.color = Color.GREEN
      console.reWrite()
      return
    
    solver.filter(word,result)
    l = len(solver.answers)
    answerCountText.text = str(l)
    if l < 30:
      answerValuesText.text = f"\n/ {' / '.join(map(lambda x: ans[x],solver.answers))}"
    best = total[solver.best]
    bestText.text = best
    console.reWrite()
    turn += 1
  else:
    bestLine.delete()
    answersLine.delete()
    if len(solver.answers) == 0:
      console.addLine().addText("not in word list")
      return
    console.addLine().addText("solved !!")
    answerLine = console.addLine()
    answerLine.addText("answer: ")
    a = answerLine.addText(total[solver.best])
    a.bold = True
    a.color = Color.GREEN
    console.reWrite()

def solveAll():
  with open(f'result{LETTER}.csv', 'w',newline="") as f:
    writer = csv.writer(f)
    for i,word in enumerate(ans):
      solver = WordleSolver(pattern)
      guess = total.index(BEST)
      turn = 1
      text = total[guess]
      while 10657 + i != guess:
        solver.filterInt(guess,check(word,total[guess]))
        guess = solver.best
        text += " > " + total[guess]
        turn += 1
      print(word)
      writer.writerow([word,turn,text])


# if __name__ == "__main__":
#   saveDat()

# solveAll()
while True:
  dialogue()
  if input("exit? (press Y for exit)") == "Y":
    break
