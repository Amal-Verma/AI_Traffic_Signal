class Manager:
  def __init__(self):
      # print("Manager initialized")
    self.test = 1

    self.counter = 0
    self.cycle_time = 100 / self.test
    self.min_time = 5 / self.test
    self.max_time = 30 / self.test
    self.halt_time = 1 / self.test
    self.prev = [0]*4

  def call(self, cars):
      # print("Manager called")
      # print(cars)
      cycle = [
          (False, True, False, False, False, False, False, True, False, False, False, False),
          (False, False, False, False, False, False, False, False, False, False, False, False),
          (False, False, False, False, True, False, False, False, False, False, True, False),
          (False, False, False, False, False, False, False, False, False, False, False, False),
          (True, True, True, False, False, False, False, False, False, False, False, True),
          (False, False, False, False, False, False, False, False, False, False, False, False),
          (False, False, True, True, True, True, False, False, False, False, False, False),
          (False, False, False, False, False, False, False, False, False, False, False, False),
          (False, False, False, False, False, True, True, True, True, False, False, False),
          (False, False, False, False, False, False, False, False, False, False, False, False),
          (False, False, False, False, False, False, False, False, True, True, True, True),
          (False, False, False, False, False, False, False, False, False, False, False, False),
      ]

    #   timer = self.prefix_sum([self.cycle_time/4]*4)
    #   return [(True, True, True, False, False, False, False, False, False, False, False, True),(False, False, True, True, True, True, False, False, False, False, False, False),(False, False, False, False, False, True, True, True, True, False, False, False),(False, False, False, False, False, False, False, False, True, True, True, True)],timer

      if (sum(cars) == 0):
        return [(True, True, True, False, False, False, False, False, False, False, False, True),(False, False, True, True, True, True, False, False, False, False, False, False),(False, False, False, False, False, True, True, True, True, False, False, False),(False, False, False, False, False, False, False, False, True, True, True, True)], self.prefix_sum([self.cycle_time/30]*4)

      t1 = self.helper([cars[0]+cars[2],cars[1]+cars[3]],(self.cycle_time-6*self.halt_time)/2)
      cars2 = [0,0,0,0]
      if all(self.prev) and all(cars):
        for i in range(4):
           cars2[i] = cars[i]+(cars[i]-self.prev[i])/self.prev[i]*cars[i]
      t2 = self.helper([cars2[0]+cars[3]/4,cars2[1]+cars[0]/4,cars2[2]+cars[1]/4,cars[3]+cars[2]/4],(self.cycle_time-6*self.halt_time)/2)
      timer = [t1[0],self.halt_time,t1[1],self.halt_time,t2[0],self.halt_time,t2[1],self.halt_time,t2[2],self.halt_time,t2[3],self.halt_time]
      
      print(timer, cars)
      
      timer = self.prefix_sum(timer)
      self.prev = cars[:]
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