#@title
# %%writefile automatic_assessment_program.py
import sys, random, math, os, traceback, gspread
from requests import get
from oauth2client.service_account import ServiceAccountCredentials
from IPython.core.display import display, HTML, Image
from jupyter_judge.problem import *
# from problem import *

#------------------------------------------------------------------------------#
#구글 스프레드시트와 연동하기
scope = ['https://spreadsheets.google.com/feeds']
# 구글 클라우드 플랫폼에서 json 파일 인증 받아야 함.
json_file_name = '/content/jupyter_judge/judge-dashboard-5145c009c952.json'
credentials = ServiceAccountCredentials.from_json_keyfile_name(json_file_name, scope)
gc = gspread.authorize(credentials)
# 개인적으로 사용할 스프레드시트 url
spreadsheet_url = 'https://docs.google.com/spreadsheets/d/1Y9eq9eP1XV9qepsgFw-NdFk0Fdw7Ut6m3LzHEZxKrMg/edit#gid=0'
#------------------------------------------------------------------------------#
# 문서 이름을 ID로 불러오기
# 학생들이 문서이름을 ID로 만들어야 함.
my_id = input('이름을 입력해주세요.')
print('지금부터 공부를 시작합니다.')
#------------------------------------------------------------------------------#
# 문서 및 시트 불러오기
doc = gc.open_by_url(spreadsheet_url)
worksheet = doc.worksheet('시트1') 

#------------------------------------------------------------------------------#

#문제 입력
#input이 없으면 입력 비워놓기

#------------------------------------------------------------------------------#

#문제에 따른 시도한 횟수를 dictionary로 만듬
trial_error_count = {}
for i in range(len(test_set)) : 
  trial_error_count[test_set[i]['test_file']] = 0

#------------------------------------------------------------------------------#

#출력할 때 글씨 색
reset = '\033[0m'
tc_red = '\033[38;2;255;0;0m'
tc_green = '\033[38;2;0;255;0m'
bc_yellow = '\033[48;2;255;255;0m'
bc_green = '\033[48;2;0;255;0m'
bc_red = '\033[48;2;255;0;m'

#------------------------------------------------------------------------------#
# 코드를 input/output 리스트에 넣기
def code_arrange(py_name) : 
  global result, code, code_input, code_input_count #, code_input_split
  result= []
  code = []
  code_input_count = 0
  code_input = []
  # code_input_split = []

  file_name = '/content/'+py_name

  f = open(file_name, 'r')  # '/content/____.py  << 이 부분은 함수 매개변수로 불러와야 함.
  lines = f.readlines()
  for line in lines : 
  #  line = line.strip()
    if line != '' : 
      code.append(line)    
      # if line.find('input().split()') >= 0 : 
      #   code_input_count += 1
      #   code_input_split.append(code.index(line))
      #   continue
      if line.find('input') >= 0 : 
        code_input_count += 1
        code_input.append(code.index(line))
  f.close()

  for i in range(len(code)) : 
    if code[i].find('\n') >= 0 : 
      code[i] = code[i][:-1]
    code[i] = code[i].rstrip()

  # print(f'code 리스트 : {code}, code 개수 : {len(code)}')
  # print(f'code_input 리스트 : {code_input}')
  # print(f'code_input_count 리스트 : {code_input_count}')

#------------------------------------------------------------------------------#
# 리스트에 있는 코드를 평가 코드로 수정하기
def code_convert(answer_input) : 
  global test_py, answer_txt, original

  f = open(test_py, 'w')  
  original = sys.stdout
  sys.stdout = f

  print('import sys')
  print(f"f = open('{answer_txt}', 'w')")
  print('original = sys.stdout')
  print('sys.stdout = f')
  try : 
    order = 0  
    count = 0

    for order in range(len(code)) : 
      if order in code_input : 
        if len(answer_input[test_count]['input'][code_input.index(order)]) == 1 : 
          replace_input =  '"'+str(answer_input[test_count]['input'][code_input.index(order)][0])+'"' 
          print(code[order].replace('input()',replace_input))
       
        else : 
          replace_input =  str(answer_input[test_count]['input'][code_input.index(order)])
          print(code[order].replace('input().split()',replace_input))  

      else : 
        print(code[order])

    print('sys.stdout = original')
    print('f.close()')

    # 파이썬 코드로 실행해야 함. 원상복구
    sys.stdout = original   
    f.close()                 
  except :  
    print('sys.stdout = original')
    print('f.close()')
    
    sys.stdout = original   
    f.close()

#------------------------------------------------------------------------------#

def code_test(answer_input) : 
  global user_answer, answer_txt, test_count
  user_answer = []
  answer_filename = '/content/'+answer_txt
  f = open(answer_filename, 'r')
  lines = f.readlines()

  for line in lines :  # 결과를 문자열로 형태로 정답 리스트에 추가한다.
    line = line.strip()
    if line != '' : 
      user_answer.append(str(line))
  f.close()

  answer_input[test_count]['output'] = list(map(str, answer_input[test_count]['output']))
  if user_answer == answer_input[test_count]['output'] : 
    result.append(True)
  else : 
    result.append(False) 

#------------------------------------------------------------------------------#
# syntax 오류 외 코드 출력창에 코드 불러오는 것
# 틀린 코드에 빨간색 표시
def code_print(py_name) :  
  file_name = '/content/'+py_name
  f = open(file_name, 'r')  # '/content/____.py  << 이 부분은 함수 매개변수로 불러와야 함.
  lines = f.readlines()
  error_count = error_line()
  code_count = 1

  for line in lines[4:-2] : 
    if error_count == code_count : 
      print(tc_red+line[:-1]+reset)
      code_count += 1
    else : 
      print(line[:-1])
      code_count += 1
  f.close()
#------------------------------------------------------------------------------#
# syntax 오류 코드 출력창에 코드 불러오는 것
# 틀린 코드에 빨간색 표시 없음
def code_print_syntax(py_name) :  
  file_name = '/content/'+py_name
  f = open(file_name, 'r')  # '/content/____.py  << 이 부분은 함수 매개변수로 불러와야 함.
  lines = f.readlines()

  for line in lines[4:-2] : 
    print(line[:-1])
  f.close()
#------------------------------------------------------------------------------#
# syntax 외 오류 라인 검출
# 오류가 몇 번째 코드에서 발생했는지 번호 호출
def error_line() : 
  trace = traceback.format_exc()
  error = ''
  line = ''
  for i in trace.split('\n') :  
    if i.find('string') >= 0 : 
      error = i.strip()    
  for i in error.split(',') : 
    if i.find('line') >= 0 : 
      line = i.strip()
  return int(line[line.find('e')+2:])-4
#------------------------------------------------------------------------------#
#에러에 따른 정보를 알려주는 함수
def name_error(test_py) : 
  sys.stdout = original   
  print(error_line(), '번째 줄에 변수 또는 명령어 이름을 확인하거나, 문자열에 따옴표가 붙어 있는지 확인하세요.')
  print("="*40)
  code_print(test_py)

def type_error(test_py) : 
  sys.stdout = original   
  print(error_line(), '번째 줄에 숫자나 문자를 바르게 입력했나요?')
  print('또는 ()안에 알맞은 숫자를 입력했나요?')
  print("="*40)
  code_print(test_py)

def attribute_error(test_py) : 
  sys.stdout = original   
  print(error_line(), '번째 줄에 라이브러리의 속성 또는 메서드를 바르게 입력했나요?')
  print("="*40)
  code_print(test_py)

def value_error(test_py) : 
  sys.stdout = original   
  print(error_line(), '번째 줄에 숫자나 문자, 입력을 바르게 입력했나요?')
  print("="*40)
  code_print(test_py)

def index_error(test_py) : 
  sys.stdout = original   
  print(error_line(), '번째 줄에 리스트나 튜플의 길이를 확인해주세요.')
  print("="*40)
  code_print(test_py)

def indentation_error(test_py) : 
  sys.stdout = original   
  print(error_line(), '번째 줄에 띄어쓰기를 확인해주세요.')     
  print("="*40)
  code_print(test_py)  

def zerodivision_error(test_py) : 
  sys.stdout = original   
  print(error_line(), '번째 줄에 숫자를 0으로 나누면 안되요.')           
  print("="*40)
  code_print(test_py)

def overflow_error(test_py) : 
  sys.stdout = original   
  print(error_line(), '번째 줄에 너무 큰 수는 표현할 수 없어요')
  print("="*40)
  code_print(test_py)

def keyboard_interrupt(test_py) : 
  sys.stdout = original   
  print('사용자가 작동 정지함.')

def syntax_error(test_py) : 
  sys.stdout = original  
  print('문법오류입니다. ":", "()"를 확인하세요')
  print("="*40)
  code_print_syntax(test_py)

def modulenotfound_error(test_py) : 
  sys.stdout = original       
  print(error_line(), '번째 줄에 라이브러리를 확인해주세요.')
  print("="*40)
  code_print(test_py)

def else_error(test_py) : 
  sys.stdout = original   
  print('코드 오류입니다.') 
  print("="*40)
  code_print(test_py)

def error_check(test_py) : 
  global compile_error
  compile_error = False
  try : 
    exec(open(test_py).read())
  except NameError : 
    name_error(test_py)
    compile_error = True
    return
  except TypeError : 
    type_error(test_py)
    compile_error = True
    return
  except AttributeError : 
    attribute_error(test_py)
    compile_error = True
    return
  except ValueError : 
    value_error(test_py)
    compile_error = True
    return
  except IndexError : 
    index_error(test_py)
    compile_error = True
    return
  except IndentationError : 
    indentation_error(test_py)
    compile_error = True
    return
  except ZeroDivisionError : 
    zerodivision_error(test_py)
    compile_error = True
    return
  except OverflowError : 
    overflow_error(test_py)
    compile_error = True
    return
  except KeyboardInterrupt : 
    keyboard_interrupt(test_py)
    compile_error = True
    return
  except SyntaxError : 
    syntax_error(test_py)
    compile_error = True
    return
  except ModuleNotFoundError : 
    modulenotfound_error(test_py)
    compile_error = True
    return
  except : 
    else_error(test_py)
    compile_error = True
    return

#------------------------------------------------------------------------------#
# 코드 결과를 구글 스프레드 시트에 보내기
def update_excel(message, py) : 
  global my_id
  name_list = worksheet.col_values(1)
  question_list = worksheet.row_values(1)  
  if my_id in name_list : 
    row = name_list.index(my_id)+1
  else : 
    row = len(name_list)+1
    worksheet.update_cell(row,1, my_id)

  # 몇 번 문제 풀었는지 확인함. 
  if py in question_list : 
    col = question_list.index(py) + 1
  else : 
    col = len(question_list) + 1
    worksheet.update_cell(1,col, py)
    worksheet.update_cell(1,col+1, '시도횟수')  

  worksheet.update_cell(row, col, message)
  worksheet.update_cell(row, col+1, trial_error_count[py])
#------------------------------------------------------------------------------#
#HTML 형식의 문제 불러오기기
def Question(question_, img="") : 
  display(HTML(question_))
  return Image(url= img) 
#------------------------------------------------------------------------------#
#코드의 정답 여부를 확인하는 함수
def code_check(py) :
  for i in range(len(test_set)) :
    if test_set[i]['test_file'] == py :
      global answer 
      answer = test_set[i]['answer']
      global question
      question = test_set[i]['question']   
  trial_error_count[py] += 1    
  try : 
    code_arrange(py)
  except : 
    print('평가 코드를 생성하세요.')
    return
  if code_input_count : 
    if code_input_count != len(answer[0]['input']) :         
      update_excel('입력 오류', py)     
      print('입력을 확인해주세요.')
      return
  # if code_input_split : 
  #   if len(code_input_split) != 1 : 
  #     update_excel('입력 오류', py)     
  #     print('입력을 확인해주세요.')    
  #     return
   
  # print(question, '\n')   
  Question('<h2 style = "background-color:yellow">결과 확인</h2>')  
  # Question(question)
  global test_count
  for test_count in range(len(answer)) : 
    global test_py, answer_txt
    test_py = 'test'+str(test_count)+'.py'
    answer_txt = 'answer'+str(test_count)+'.txt'
    code_convert(answer)
    error_check(test_py)
    # 코드 실행 시 오류발생하면 확인 종료
    if compile_error == True :
      try : 
        update_excel('오류입니다.', py)     
        return    
      except : 
        return    

    code_test(answer)        
    #입력이 없는 문제
    if len(answer[0]['input']) == 0 : 
      if result[test_count] == True : 
        Question('<li>처리한 데이터 : </li>') 
        for i in user_answer : 
          if i == user_answer[-1] : 
            print(bc_yellow+str(i)+reset,tc_green+'O'+reset)
          else : 
            print(bc_yellow+str(i)+reset)
      else :
        Question('<li>처리한 데이터 : </li>') 
        for i in user_answer : 
          if i == user_answer[-1] : 
            print(bc_yellow+str(i)+reset, tc_red+'X'+reset)
          else : 
            print(bc_yellow+str(i)+reset)
    else :  
    #입력이 있는 문제
      if result[test_count] == True : 
        Question('<li>입력한 데이터 : </li>') 
        for i in answer[test_count]['input'] :    
          if len(i) == 1 : 
            print(i[0])
          else : 
            for j in i : 
              if j == i[-1] : 
                print(j, end = '\n')
              else : 
                print(j, end = ' ')              

        # for i in answer[test_count]['input'] : print(i)
        Question('<li>처리한 데이터 : </li>') 
        for i in user_answer : 
          if i == user_answer[-1] : 
            print(bc_yellow+str(i)+reset, tc_green+'O'+reset)
          else : 
            print(bc_yellow+str(i)+reset)
      else : 
        Question('<li>입력한 데이터 : </li>') 
        for i in answer[test_count]['input'] :    
          if len(i) == 1 : 
            print(i[0])
          else : 
            for j in i : 
              if j == i[-1] : 
                print(j, end = '\n')
              else : 
                print(j, end = ' ')              

        Question('<li>처리한 데이터 : </li>') 
        for i in user_answer : 
          if i == user_answer[-1] : 
            print(bc_yellow+str(i)+reset,tc_red+'X'+reset)
          else : 
            print(bc_yellow+str(i)+reset)
    Question('<HR>')
  if sum(result) == test_count+1 :
    try : 
      update_excel('정답입니다.', py)
      print(tc_green+'정답입니다.'+reset)
    except : 
      print(tc_green+'정답입니다.'+reset)
  else : 
    try : 
      update_excel('틀렸습니다.', py)
      print(tc_red+'틀렸습니다.'+reset)
    except : 
      print(tc_red+'틀렸습니다.'+reset)
