#!/usr/bin/env python
# -*- coding: utf-8 -*-
class Bot():
  #ここに素数判定プログラムを実装してください。

  # Please write your code here.[
  def __init__(self, command):
    self.command = command['command']
    self.data = command['data']

  def generate_hash(self):
    command_ord = ""
    data_ord = ""
    for w in self.command:
      command_ord += str(ord(w))
    c_ord_n = int(command_ord)
    if len(command_ord) >= 22:
      result = self.scientificNotation(c_ord_n)
      c_ord_n = int("".join(result.replace("1.", "").split("e+")))
      
    for w in self.data:
      data_ord += str(ord(w))
    d_ord_n = int(data_ord)
    if len(data_ord) >= 22:
      result = self.scientificNotation(d_ord_n)
      d_ord_n = int("".join(result.replace("1.", "").split("e+")))
    
    self.hash = format(c_ord_n+d_ord_n, 'x')
    
      

  # Convert the number into scientific notation with 16 digits after "."
  # If power of e is greater than 20, get the number between "." and "e"
  # Else return the number itself
  def scientificNotation(self, num):
    data = "%.16e" % num
    result = data if (int(data.split("e+")[1]) > 20) else num
    return result
