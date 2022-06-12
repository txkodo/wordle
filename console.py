from __future__ import annotations
from enum import Enum
from sre_parse import State
from typing import Callable
import sys

class Console:
  def __init__(self) -> None:
    self.result = None
    self.lines:list[ConsoleLine] = []

  def reWrite(self):
    if self.result is not None:
      self.deleteUpperLines(self.result.count("\n")+1)
    self.result = '\n'.join(map(str,self.lines))
    print(self.result)
  
  def addLine(self):
    l = ConsoleLine(self)
    self.lines.append(l)
    return l
  
  def deleteUpperLines(self,count:int=1):
    for _ in range(count):
      sys.stdout.write("\033[F")
      sys.stdout.write("\033[K")

  def getInput(self,message:str,reMessage:Callable[[str],str],validatior:Callable[[str],bool]) -> str:
    print(message)
    value = None
    while value is None or not validatior(value):
      value = input()
      self.deleteUpperLines(2)
      print(reMessage(value))
    else:
      self.deleteUpperLines(1)
    return value

  def remove(self,line:ConsoleLine):
    self.lines.remove(line)

class ConsoleLine:
  def __init__(self,console:Console) -> None:
    self.console = console
    self.texts:list[ConsoleText] = []
  
  def addText(self,text:str=""):
    t = ConsoleText(self,text)
    self.texts.append(t)
    return t
  
  def remove(self,text:ConsoleText):
    self.texts.remove(text)
  
  def delete(self):
    self.console.remove(self)
  
  def __str__(self) -> str:
    return ''.join(map(str,self.texts))

class Color(Enum):
  BLACK     = '\033[30m'
  RED       = '\033[31m'
  GREEN     = '\033[32m'
  YELLOW    = '\033[33m'
  BLUE      = '\033[34m'
  PURPLE    = '\033[35m'
  CYAN      = '\033[36m'
  WHITE     = '\033[37m'

class State(Enum):
  BOLD = '\033[1m'
  END  = '\033[0m'

class ConsoleText:
  def __init__(self,line:ConsoleLine,text:str = "") -> None:
    self.line = line
    self.text = text
    self.color:Color|None = None
    self.bold = False

  def delete(self):
    self.line.remove(self)
  
  def setColor(self,color:Color|None = None):
    self.color = color

  def __str__(self) -> str:
    return ('\033[1m' if self.bold else '') + (self.color.value if self.color else '') + self.text + State.END.value
