class TitleQueue(object):
    def __init__(self, maxsize):
        self._usedPositions = 0
        self._maxsize = maxsize
        self._dataset = [None] * self._maxsize
        self._front = 0
        self._rear = 0

    def getUsedPositions(self):
        return self._usedPostions

    def getMaxsize(self):
        return self._maxsize

    def getFront(self):
        return self._front

    def getRear(self):
        return self._rear

    def getDataset(self):
        return self._dataset

    def incrementUsedPositions(self):
        self._usedPositions += 1

    def decrementUsedPositions(self):
        self._usedPositions -= 1

    def setFront(self):
        front += 1

    def isFull(self):
        if self._usedPositions == self._maxsize:
            return True

    def isEmpty(self):
        if self._usedPositions == 0:
            return True
        else:
            return False

    def enqueue(self, data):
        if self.isFull() == True:
            return "Queue is full"

        if self._usedPositions > 0:
            self._rear += 1

        self._dataset[rear] = data
        self.incrementUsedPositions()

    def dequeue(self):
        data = None

        if self.isEmpty() == True:
            return "Queue is empty"

        data = dataset[front]
        if self._front == self._rear:
            self._front = 0
            self._rear = 0
            usedPositions = 0
        else:
            self._front += 1
            self.decrementUsedPositions()

class TitlePriorityQueue(TitleQueue):
    def __init__(self,maxsize):
        super.new(maxsize)

    def heapSort(self, user):
        #gets length of dataset
        n = self.getFront() - self.getRear()
        #creates arbitary scores for titles which have not yet been rated by the user based on user profile data
        setGenreScores(user)

        #creates a maximum heap
        for i in range(n//2, -1):
            i -= 1

        #heap sorts elements
        for j in range(n-1, self.getRear(), -1):
            temp = self.getDataset()[j]
            self.getDataset()[j] = getDataset()[self.getRear()]
            self.getDataset()[self.getRear()] = temp
            self.heapify(self.getDataset(), j, self.getRear())

        #updates dataset into the main program
        return self.getDataset()

    def heapify(self, dataset, n, index):
        #sets up heap, with largest element as the root
        largest = root
        left = 2 * index + 1
        right = 2 * index + 2

        #checks if the left child of the root exists and if its greater than the root

        if left < n and dataset[largest].getPriorityScore() < dataset[left].getPriorityScore():
            largest = left

        #checks if the right child of the root exists and if its greater than the root
        if right < n and dataset[largest].getPriorityScore() < dataset[right].getPriorityScore():
            largest = right

        #changes root if needed
        if largest != root:
            temp = dataset[index]
            dataset[index] = dataset[largest]
            dataset[largest] = index

        #recursive call of function until fully sorted
        heapify(datatset, n, largest)
            
