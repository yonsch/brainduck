class Machine:
    def __init__(self, program):
        self.memory = [0]*100
        self.program = []
        for character in program:
            self.program.append(character)
        self.data_pointer = 0
        self.instruction_pointer = -1
        self.buffer = [0]*20

    def inc(self):
        self.memory[self.data_pointer] += 1

    def dec(self):
        self.memory[self.data_pointer] -= 1

    def forward(self):
        self.data_pointer += 1

    def backward(self):
        self.data_pointer -= 1

    def read(self):
        self.memory[self.data_pointer] = self.buffer[0]
        for c in range(19):
            self.buffer[c] = self.buffer[c+1]
        self.buffer[19] = 0

    def in_loop(self):
        if self.memory[self.data_pointer] <= 0:
            count = 1
            while count > 0:
                self.instruction_pointer += 1
                if self.memory[self.data_pointer] == '[':
                    count += 1
                if self.memory[self.data_pointer] == ']':
                    count -= 1

    def out_loop(self):
        if self.memory[self.data_pointer] > 0:
            count = 1
            while count > 0:
                self.instruction_pointer -= 1
                if self.program[self.instruction_pointer] == '[':
                    count -= 1
                if self.program[self.instruction_pointer] == ']':
                    count += 1

    def tick(self):
        self.instruction_pointer += 1
        if self.instruction_pointer == len(self.program):
            return 0
        command = self.program[self.instruction_pointer]
        if command == '>':
            self.forward()
        elif command == '<':
            self.backward()
        elif command == '+':
            self.inc()
        elif command == '-':
            self.dec()
        elif command == '[':
            self.in_loop()
        elif command == ']':
            self.out_loop()
        else:
            self.instruction_pointer += 1

    def reset(self):
        self.program = ''
        self.memory = [0]*100
        self.instruction_pointer = 0
        self.data_pointer = 0
