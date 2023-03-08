

class Node:
    def __init__(self, content):
        self.value = content
        self.next = None
        self.previousious = None

    def __str__(self):
        return ('CONTENT:{}\n'.format(self.value))

    __repr__=__str__


class ContentItem:
    '''
        >>> content1 = ContentItem(1000, 10, "Content-Type: 0", "0xA")
        >>> content2 = ContentItem(1004, 50, "Content-Type: 1", "110010")
        >>> content3 = ContentItem(1005, 18, "Content-Type: 2", "<html><p>'CMPSC132'</p></html>")
        >>> content4 = ContentItem(1005, 18, "another header", "111110")
        >>> hash(content1)
        0
        >>> hash(content2)
        1
        >>> hash(content3)
        2
        >>> hash(content4)
        1
    '''
    def __init__(self, cid, size, header, content):
        self.cid = cid
        self.size = size
        self.header = header
        self.content = content

    def __str__(self):
        return f'CONTENT ID: {self.cid} SIZE: {self.size} HEADER: {self.header} CONTENT: {self.content}'

    __repr__=__str__

    def __eq__(self, other):
        if isinstance(other, ContentItem):
            return self.cid == other.cid and self.size == other.size and self.header == other.header and self.content == other.content
        return False

    def __hash__(self):
        #Finds ord of all inputs and adds them up then divides by modulo 3
        sum = 0
        for str in self.header:
            sum += ord(str)
        return sum % 3



class CacheList:
    ''' 
        # An extended version available on Canvas. Make sure you pass this doctest first before running the extended version

        >>> content1 = ContentItem(1000, 10, "Content-Type: 0", "0xA")
        >>> content2 = ContentItem(1004, 50, "Content-Type: 1", "110010")
        >>> content3 = ContentItem(1005, 180, "Content-Type: 2", "<html><p>'CMPSC132'</p></html>")
        >>> content4 = ContentItem(1006, 18, "another header", "111110")
        >>> content5 = ContentItem(1008, 2, "items", "11x1110")
        >>> lst=CacheList(200)
        >>> lst
        REMAINING SPACE:200
        ITEMS:0
        LIST:
        <BLANKLINE>
        >>> lst.put(content1, 'mru')
        'INSERTED: CONTENT ID: 1000 SIZE: 10 HEADER: Content-Type: 0 CONTENT: 0xA'
        >>> lst.put(content2, 'lru')
        'INSERTED: CONTENT ID: 1004 SIZE: 50 HEADER: Content-Type: 1 CONTENT: 110010'
        >>> lst.put(content4, 'mru')
        'INSERTED: CONTENT ID: 1006 SIZE: 18 HEADER: another header CONTENT: 111110'
        >>> lst.put(content5, 'mru')
        'INSERTED: CONTENT ID: 1008 SIZE: 2 HEADER: items CONTENT: 11x1110'
        >>> lst.put(content3, 'lru')
        "INSERTED: CONTENT ID: 1005 SIZE: 180 HEADER: Content-Type: 2 CONTENT: <html><p>'CMPSC132'</p></html>"
        >>> lst.put(content1, 'mru')
        'INSERTED: CONTENT ID: 1000 SIZE: 10 HEADER: Content-Type: 0 CONTENT: 0xA'
        >>> 1006 in lst
        True
        >>> contentExtra = ContentItem(1034, 2, "items", "other content")
        >>> lst.update(1008, contentExtra)
        'UPDATED: CONTENT ID: 1034 SIZE: 2 HEADER: items CONTENT: other content'
        >>> lst
        REMAINING SPACE:170
        ITEMS:3
        LIST:
        [CONTENT ID: 1034 SIZE: 2 HEADER: items CONTENT: other content]
        [CONTENT ID: 1006 SIZE: 18 HEADER: another header CONTENT: 111110]
        [CONTENT ID: 1000 SIZE: 10 HEADER: Content-Type: 0 CONTENT: 0xA]
        <BLANKLINE>
        >>> lst.tail.value
        CONTENT ID: 1000 SIZE: 10 HEADER: Content-Type: 0 CONTENT: 0xA
        >>> lst.tail.previous.value
        CONTENT ID: 1006 SIZE: 18 HEADER: another header CONTENT: 111110
        >>> lst.tail.previous.previous.value
        CONTENT ID: 1034 SIZE: 2 HEADER: items CONTENT: other content
        >>> lst.tail.previous.previous is lst.head
        True
        >>> lst.tail.previous.previous.previous is None
        True
        >>> lst.clear()
        'Cleared cache!'
        >>> lst
        REMAINING SPACE:200
        ITEMS:0
        LIST:
        <BLANKLINE>
       
    '''
    def __init__(self, size):
        self.head = None
        self.tail = None
        self.maxSize = size
        self.remainingSpace = size
        self.numItems = 0

    def __str__(self):
        listString = ""
        current = self.head
        while current is not None:
            listString += "[" + str(current.value) + "]\n"
            current = current.next
        return 'REMAINING SPACE:{}\nITEMS:{}\nLIST:\n{}'.format(self.remainingSpace, self.numItems, listString)  

    __repr__=__str__

    def __len__(self):
        return self.numItems
    
    def put(self, content, evictionPolicy):
        #If size to big : error
        if content.size > self.maxSize:
            return 'Insertion not allowed'
        #If content already in list
        elif self.__contains__(content.cid):
            return 'Content {} already in cache, insertion not allowed'.format(content.cid)
        #updates remainingSpace as if content has been added
        self.remainingSpace -= content.size
        #Clears up space by deleting content from head/tail
        while self.remainingSpace < 0:
            if evictionPolicy == 'lru':
                self.lruEvict()
            elif evictionPolicy == 'mru':
                self.mruEvict()
        #If Cache cleared updates remaining space
        if self.remainingSpace == self.maxSize:
            self.remainingSpace -= content.size
        
        #Adds Content to beggining of list
        nNode = Node(content)
        if self.head == None:
            self.head = nNode
            self.tail = nNode
            nNode.previous = None
            nNode.next = None
        else:
            nNode.next = self.head
            self.head.previous = nNode
            nNode.previous = None
            self.head = nNode
        self.numItems+=1
        return 'INSERTED: {}'.format(nNode.value)

    def updateRemSpace(self):
        #Updates remaining space by reseting it and adding all sizes of linked list
        current = self.head
        self.remainingSpace = self.maxSize
        while current != None:
            self.remainingSpace -= current.value.size
            current = current.next
        
    

    def __contains__(self, cid):
        #Searches every node of linked list for cid, if found moves the node with cid to the head of the list and returns True, if not found returns False
        #Returns False if list empty
        if self.head == None:
            return False
        current = self.head
        #Go over entire list looking for cid in every node
        while current != None:
            if current.value.cid == cid:
                #If node is head do not move
                if self.head.value == current.value:
                    return True
                self.MoveToFront(current)
                return True
            current = current.next
        #Return false if cid not found
        return False


    def update(self, cid, content):
        #self.__contatins__ moves ContentItem with cid to front if found
        if self.__contains__(cid):
            #If new data causes list to exceed max size
            if self.remainingSpace < content.size - self.head.value.size:
                return 'Cache miss!'

            #Changes attributes of ContentItem with cid to attributes of content
            self.head.value.size = content.size
            self.head.value.header = content.header
            self.head.value.content = content.content
            self.head.value.cid = content.cid
            #Updates Remaining Space
            self.updateRemSpace()
            return 'UPDATED: {}'.format(self.head.value)
        else:
            return 'Cache miss!'


    
    def MoveToFront(self, cNode):
        if self.head.value == cNode.value:
            return
        #If node is tail, update accordingly
        elif self.tail.value == cNode.value:
            cNode.previous.next = None
            self.tail = cNode.previous
        #If node in between head and tail
        #Sets node pointers in front and behind current to each other
        else:
            cNode.previous.next = cNode.next
            cNode.next.previous = cNode.previous
        #Update node with cid and head accordingly
        cNode.next = self.head
        cNode.previous = None
        self.head.previous = cNode
        self.head = cNode
   
        


    def mruEvict(self):
        #if 0 items : return, 1 item : clear cache, 2 item : get rid of head and update list
        if self.head == None:
            return 
        elif self.head.value == self.tail.value:
            self.clear()
        else:
            self.remainingSpace += self.head.value.size
            self.head = self.head.next
            self.head.previous = None
            self.numItems -= 1

    def lruEvict(self):
        #if 0 items : return, 1 item : clear cache, 2 item : get rid of tail and update list
        if self.head == None:
            return
        elif self.head.value == self.tail.value:
            self.clear()
        else:
            self.remainingSpace += self.tail.value.size
            self.tail = self.tail.previous
            self.tail.next = None
            self.numItems -= 1

    def clear(self):
        #Resets all values
        self.head = None
        self.tail = None
        self.remainingSpace = self.maxSize
        self.numItems = 0
        return 'Cleared cache!'


class Cache:
    """
        # An extended version available on Canvas. Make sure you pass this doctest first before running the extended version

        >>> cache = Cache()
        >>> content1 = ContentItem(1000, 10, "Content-Type: 0", "0xA")
        >>> content2 = ContentItem(1003, 13, "Content-Type: 0", "0xD")
        >>> content3 = ContentItem(1008, 242, "Content-Type: 0", "0xF2")

        >>> content4 = ContentItem(1004, 50, "Content-Type: 1", "110010")
        >>> content5 = ContentItem(1001, 51, "Content-Type: 1", "110011")
        >>> content6 = ContentItem(1007, 155, "Content-Type: 1", "10011011")

        >>> content7 = ContentItem(1005, 18, "Content-Type: 2", "<html><p>'CMPSC132'</p></html>")
        >>> content8 = ContentItem(1002, 14, "Content-Type: 2", "<html><h2>'PSU'</h2></html>")
        >>> content9 = ContentItem(1006, 170, "Content-Type: 2", "<html><button>'Click Me'</button></html>")

        >>> cache.insert(content1, 'lru')
        'INSERTED: CONTENT ID: 1000 SIZE: 10 HEADER: Content-Type: 0 CONTENT: 0xA'
        >>> cache.insert(content2, 'lru')
        'INSERTED: CONTENT ID: 1003 SIZE: 13 HEADER: Content-Type: 0 CONTENT: 0xD'
        >>> cache.insert(content3, 'lru')
        'Insertion not allowed'

        >>> cache.insert(content4, 'lru')
        'INSERTED: CONTENT ID: 1004 SIZE: 50 HEADER: Content-Type: 1 CONTENT: 110010'
        >>> cache.insert(content5, 'lru')
        'INSERTED: CONTENT ID: 1001 SIZE: 51 HEADER: Content-Type: 1 CONTENT: 110011'
        >>> cache.insert(content6, 'lru')
        'INSERTED: CONTENT ID: 1007 SIZE: 155 HEADER: Content-Type: 1 CONTENT: 10011011'

        >>> cache.insert(content7, 'lru')
        "INSERTED: CONTENT ID: 1005 SIZE: 18 HEADER: Content-Type: 2 CONTENT: <html><p>'CMPSC132'</p></html>"
        >>> cache.insert(content8, 'lru')
        "INSERTED: CONTENT ID: 1002 SIZE: 14 HEADER: Content-Type: 2 CONTENT: <html><h2>'PSU'</h2></html>"
        >>> cache.insert(content9, 'lru')
        "INSERTED: CONTENT ID: 1006 SIZE: 170 HEADER: Content-Type: 2 CONTENT: <html><button>'Click Me'</button></html>"
        >>> cache
        L1 CACHE:
        REMAINING SPACE:177
        ITEMS:2
        LIST:
        [CONTENT ID: 1003 SIZE: 13 HEADER: Content-Type: 0 CONTENT: 0xD]
        [CONTENT ID: 1000 SIZE: 10 HEADER: Content-Type: 0 CONTENT: 0xA]
        <BLANKLINE>
        L2 CACHE:
        REMAINING SPACE:45
        ITEMS:1
        LIST:
        [CONTENT ID: 1007 SIZE: 155 HEADER: Content-Type: 1 CONTENT: 10011011]
        <BLANKLINE>
        L3 CACHE:
        REMAINING SPACE:16
        ITEMS:2
        LIST:
        [CONTENT ID: 1006 SIZE: 170 HEADER: Content-Type: 2 CONTENT: <html><button>'Click Me'</button></html>]
        [CONTENT ID: 1002 SIZE: 14 HEADER: Content-Type: 2 CONTENT: <html><h2>'PSU'</h2></html>]
        <BLANKLINE>
        <BLANKLINE>
        >>> cache[content9].next.value
        CONTENT ID: 1002 SIZE: 14 HEADER: Content-Type: 2 CONTENT: <html><h2>'PSU'</h2></html>
        
    """

    def __init__(self):
        self.hierarchy = [CacheList(200), CacheList(200), CacheList(200)]
        self.size = 3
    
    def __str__(self):
        return ('L1 CACHE:\n{}\nL2 CACHE:\n{}\nL3 CACHE:\n{}\n'.format(self.hierarchy[0], self.hierarchy[1], self.hierarchy[2]))
    
    __repr__=__str__


    def clear(self):
        for item in self.hierarchy:
            item.clear()
        return 'Cache cleared!'

    
    def insert(self, content, evictionPolicy):
        #Gets hash and corresponding list
        hValue = hash(content)
        hValList = self.hierarchy[hValue]
        #Inserts content into list
        return hValList.put(content, evictionPolicy)


    def __getitem__(self, content):
        #Gets hash and corresponding list
        hValue = hash(content)
        hValList = self.hierarchy[hValue]
        #call __contains__ function and if it works the head is now the value we want
        if content.cid in hValList:
            return hValList.head
        else:
            return 'Cache miss!'



    def updateContent(self, content):
        #Gets hash and corresponding list
        hValue = hash(content)
        hValList = self.hierarchy[hValue]
        #Updates respective list
        ret_val = hValList.update(content.cid, content)
        #Since the output is specific to this function and based on the .update function I saved the .update function's return to a variable and used that to determine this function's return 
        if ret_val == "Cache miss!":
            return ret_val
        else:
            return hValList.head.value
        

if __name__=='__main__':
    import doctest
    doctest.testmod()
    #doctest.run_docstring_examples(Cache, globals(), name='HW4_EXTENDED DOCTEST.py',verbose=True) 