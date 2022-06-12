from math import log2
from pathlib import Path
import csv
import re

from console import Color, Console

def getAnswers():
  return Path("5answer.txt").read_text().split()

def getGuesses():
  return Path("5guess.txt").read_text().split()

def resultToStr(result:int):
  r = ""
  for _ in range(5):
    r += "⬛🟨🟩"[result % 3]
    result //= 3
  return r

def check(ans:str,choice:str) -> int:
  a:list[str] = list(ans)
  # 0 含まれていない
  # 1 位置は違う
  # 2 位置まで一致
  result = [0,0,0,0,0]
  for i in range(5):
    if a[i] == choice[i]:
      result[i] = 2
      a[i] = '*'
  for i in range(5):
    if a[i] != '*':
      try:
        j = a.index(choice[i])
        result[i] = 1
        a[j] = '#'
      except ValueError:
        continue
  r = ( result[0] + result[1] * 3 + result[2] * 9 + result[3] * 27 + result[4] * 81 )
  return r

def saveCsv():
  ans = getAnswers()
  guess = getGuesses()

  with open('pattern5.csv', 'w') as f:
    w = csv.writer(f)
    for i in guess + ans:
      w.writerow([check(j,i) for j in ans])

# saveCsv()

def loadCsv():
  with open('pattern5.csv', 'r') as f:
    list = [row for row in csv.reader(f)]
  return list

# ans 2315
# guess 10657 
# total 12972

  
ans = getAnswers()
guess = getGuesses()
total = guess + ans

pattern = [[ int(j) for j in i ] for i in loadCsv()]

class WordleSolver:
  def __init__(self,pattern:list[list[int]]) -> None:
    self.pattern = pattern
    self.answers = set(range(2315))
    self.guesses = range(12972)
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
    patterns = [0] * 243
    w = self.pattern[word]
    for i in self.answers:
      patterns[w[i]] += 1
    
    p = [ patterns[i] / 12972 for i in range(243) ]
    potential = sum( 0 if i == 0 else i * log2(1/i) for i in p )

    return potential
  
  def getBestWord(self) -> int:
    if len(self.answers) == 1:
      self._best = 10657 + self.answers.pop()
      return self._best
    word = 0
    max = 0
    for guess in self.guesses:
      w = self.getWordPotential(guess)
      if w > max or ( w == max and guess - 10657 in self.answers ):
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

def dialogue():
  solver = WordleSolver(pattern)
  best = "soare"
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
    resultChars = [results.addText(word[i]) for i in range(5)]
    console.reWrite()

    result = console.getInput(
      "...input result e.g. 'nhjnh'",
      lambda w:f"...input result e.g. 'nhjnh' ('{w}' is not valid)",
      lambda w: re.fullmatch("[nhj]{5}",w) != None
    )

    colorMap = {
      'n': Color.WHITE,
      'h': Color.YELLOW,
      'j': Color.GREEN
    }
    for char,state in zip(resultChars,result):
      char.bold = True
      char.color = colorMap[state]
    
    if result == "jjjjj":
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
    console.addLine().addText("solved !!")
    answerLine = console.addLine()
    answerLine.addText("answer: ")
    a = answerLine.addText(total[solver.best])
    a.bold = True
    a.color = Color.GREEN
    console.reWrite()

def solveAll():
  with open('result.csv', 'w',newline="") as f:
    writer = csv.writer(f)
    for i,word in enumerate(ans):
      solver = WordleSolver(pattern)
      guess = 8530
      turn = 1
      text = total[guess]
      while 10657 + i != guess:
        solver.filterInt(guess,check(word,total[guess]))
        guess = solver.best
        text += " > " + total[guess]
        turn += 1
      print(word)
      writer.writerow([word,turn,text])

# solveAll()
while True:
  dialogue()
  if input("exit? (press Y for exit)") == "Y":
    break
