SIG_STATES = {
  'A' : (False, True, True, False, False, False, False, False, False, False, False, False),
  'B' : (False, False, False, False, False, False, False, True, True, False, False, False),
  'C' : (True, False, False, False, False, False, False, False, False, False, False, True),
  'D' : (False, False, False, False, False, True, True, False, False, False, False, False),
  'E' : (False, False, False, False, False, False, False, False, False, False, True, True),
  'F' : (False, False, False, False, True, True, False, False, False, False, False, False),
  'G' : (False, False, False, False, False, False, False, False, True, True, False, False),
  'H' : (False, False, False,True, False, False, False, False, False, False, False, False),
  'X' : (False, False, True, False, False, False, False, False, False, False, False, False)
}
NEBS = {
  'A':'D',
  'B':'C',
  'C':'B',
  'D':'A',
  'E':'H',
  'F':'G',
  'G':'F',
  'H':'E' 
}
OPPS = {
  'A':['B','C'],
  'B':['A','D'],
  'C':['A','D'],
  'D':['B','C'],
  'E':['F','G'],
  'F':['E','H'],
  'G':['E','H'],
  'H':['F','G']
}

class Manager:
  def __init__(self):
      # print("Manager initialized")
    self.test = 1

    self.counter = 0
    self.cycle_time = 100 / self.test
    self.min_time = 5 / self.test
    self.max_time = 30 / self.test
    self.halt_time = 2 / self.test
    self.prev = [0]*4
    self.isfirstcycle = True

  def call(self, cars, lanewiseCount):
    if (sum(cars) == 0):
        return [(True, True, True, False, False, False, False, False, False, False, False, True),(False, False, True, True, True, True, False, False, False, False, False, False),(False, False, False, False, False, True, True, True, True, False, False, False),(False, False, False, False, False, False, False, False, True, True, True, True)], self.prefix_sum([self.cycle_time/40]*4)
    
    if(self.isfirstcycle):
      cars = [3,3,3,3]
      lanewiseCount = [[1,1,1],[1,1,1],[1,1,1],[1,1,1]] 
      self.isfirstcycle = False
    
    vals1,vals2 = self.getValDicts(lanewiseCount)
    c1 = cars[0] + cars[2]
    c2 = cars[1] + cars[3]
    t1 = self.cycle_time * (c1 / sum(cars))
    t2 = self.cycle_time * (c2 / sum(cars))
    t1,t2 = self.adjust_two_numbers([t1,t2])
    
    sig_list1 = self.make_sig_list(vals1)
    sig_list2 = self.make_sig_list(vals2)
    cycle1 = self.getcycle(sig_list1)
    cycle2 = self.getcycle(sig_list2)
    timer1 = self.getTimer(sig_list1,t1,c1,vals1)
    timer2 = self.getTimer(sig_list2,t2,c2,vals2)
    cycle = cycle1 + cycle2
    timer = timer1 + timer2
    timer = self.prefix_sum(timer)
    print(f"Vals1 : {vals1}")
    print(f"siglist1 : {sig_list1}")
    print(f"Timer1 : {timer1}")
    print("")
    print(f"Vals2 : {vals2}")
    print(f"siglist2 : {sig_list2}")
    print(f"Timer2 : {timer2}")
    return cycle,timer
      
  
  def getValDicts(self,lanewiseCount):
    [[C,A,_],[H,F,_],[D,B,_],[G,E,_]] = lanewiseCount
    return {
        'A' : A, 'B' : B, 'C' : C, 'D' : D
    },{
      'E' : E, 'F' : F, 'G' : G, 'H' : H
    }
    
  def sig_or(self,state1,state2):
    res = [state1[i] or state2[i] for i in range(len(state1))]
    return res

  def getstate(self,sig):
    state = (False, False, False, False, False, False, False, False, False, False, False, False)
    for c in sig:
      state = self.sig_or(state,SIG_STATES[c])
    return state

  def getcycle(self,sig_list):
    cycle = []
    for sig in sig_list:
      cycle.append(self.getstate(sig))
    cycle.append(SIG_STATES['X'])
    return cycle

  def myfun1(self,a,b):
    '''Returns the letter which is in a but not in b'''
    return (set(a) - set(b)).pop()
  
  def getTimer(self,sig_list,avail_time,tot_cars,vals):
    avail_time -=  self.halt_time
    tx = self.halt_time
    if tot_cars == 0:
      td = avail_time / 3
      return [td,td,td,tx]
    t1 = avail_time * (vals[self.myfun1(sig_list[0],sig_list[1])] / tot_cars)
    t3 = avail_time * (vals[self.myfun1(sig_list[2],sig_list[1])] / tot_cars)
    t2 = avail_time - t1 - t3
    t1,t2,t3 = self.adjust_distribution([t1,t2,t3])
    timer = [t1,t2,t3,tx]
    return timer
  
  def make_sig_list(self,vals):
    maxKey = list(vals.keys())[0]
    for key in vals:
      if vals[key] > vals[maxKey]:
        maxKey = key
    sig_list = []
    opp = OPPS[maxKey]
    if(vals[opp[0]] > vals[opp[1]]):
      sig_list.append(maxKey + opp[1])
      sig_list.append(maxKey + opp[0])
      sig_list.append(NEBS[maxKey] + opp[0])
    else:
      sig_list.append(maxKey + opp[0])
      sig_list.append(maxKey + opp[1])
      sig_list.append(NEBS[maxKey] + opp[1])
    return sig_list
  
  def helper(self, cars,cycle):
      if (sum(cars) == 0):
          return [cycle/len(cars)]*len(cars)
      timer = [(self.min_time + ((cycle - len(cars) *
                self.min_time) * car / (sum(cars)))) for car in cars]

      if (max(timer) > self.max_time):
          timer = [min(time+(max(timer)-self.max_time)/3, self.max_time)
                    for time in timer]

      return timer
  
  def adjust_distribution(self,arr):
    total = sum(arr)
    min_limit = 0.3 * total
    if arr[0] < min_limit:
        diff = min_limit - arr[0]
        arr[0] += diff
        arr[1] -= diff
    if arr[2] < min_limit:
        diff = min_limit - arr[2]
        arr[2] += diff
        arr[1] -= diff
    
    return arr
  
  def adjust_two_numbers(self,arr):
    total = sum(arr)
    min_limit = 0.2 * total

    if arr[0] < min_limit:
        diff = min_limit - arr[0]
        arr[0] += diff
        arr[1] -= diff
    elif arr[1] < min_limit:
        diff = min_limit - arr[1]
        arr[1] += diff
        arr[0] -= diff
    
    return arr

  def prefix_sum(self, arr):
    for i in range(1, len(arr)):
        arr[i] += arr[i-1]
    return arr