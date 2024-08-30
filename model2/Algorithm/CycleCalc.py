class Manager:
  def __init__(self):
      # print("Manager initialized")
      self.counter = 0
      self.cycle_time = 10
      self.min_time = 0.5
      self.max_time = 3

  def call(self, cars):
      # print("Manager called")
      # print(cars)
      cycle = [
          (False, True, True, False, False, True, False, True, True, False, False, True),
          (False, False, False, False, False, False, False, False, False, False, False, False),
          (False, False, True, False, True, True, False, False, True, False, True, True),
          (False, False, False, False, False, False, False, False, False, False, False, False),
          (True, True, True, False, False, True, False, False, True, False, False, True),
          (False, False, False, False, False, False, False, False, False, False, False, False),
          (False, False, True, True, True, True, False, False, True, False, False, True),
          (False, False, False, False, False, False, False, False, False, False, False, False),
          (False, False, True, False, False, True, True, True, True, False, False, True),
          (False, False, False, False, False, False,False, False, False, False, False, False),
          (False, False, True, False, False, True, False, False, True, True, True, True),
          (False, False, False, False, False, False, False, False, False, False, False, False),
      ]

      if (sum(cars) == 0):
          return cycle, self.prefix_sum([self.cycle_time/len(cars)]*len(cars))

      t1 = self.helper([cars[0]+cars[2],cars[1]+cars[3]],(self.cycle_time-8)/2)
      t2 = self.helper(cars,(self.cycle_time-8)/2)
      timer = [t1[0],1,t1[1],1,t2[0],1,t2[1],1,t2[2],1,t2[3],1]
      
      print(timer, cars)
      
      timer = self.prefix_sum(timer)

      return cycle, timer

  def helper(self, cars,cycle):
      if (sum(cars) == 0):
          return [cycle/len(cars)]*len(cars)
      timer = [(self.min_time + ((cycle - len(cars) *
                self.min_time) * car / (sum(cars)))) for car in cars]

      if (max(timer) > self.max_time):
          timer = [min(time+(max(timer)-self.max_time)/3, self.max_time)
                    for time in timer]

      return timer

  def prefix_sum(self, arr):
    for i in range(1, len(arr)):
        arr[i] += arr[i-1]
    return arr