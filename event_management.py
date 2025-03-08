import datetime

class EventNode:
    def __init__(self, event_ID, start_time, end_time, event_name):
        self.event_ID = event_ID
        self.start_time = start_time 
        self.end_time = end_time 
        self.event_name = event_name
        self.height = 1
        self.left = None
        self.right = None

class AVLTree:    
    def get_height(self, node):
        return node.height if node else 0

    def get_balance(self, node):
        return self.get_height(node.left) - self.get_height(node.right) if node else 0

    def rotate_right(self, y):
        x = y.left
        T2 = x.right
        x.right = y
        y.left = T2
        y.height = 1 + max(self.get_height(y.left), self.get_height(y.right))
        x.height = 1 + max(self.get_height(x.left), self.get_height(x.right))
        return x

    def rotate_left(self, x):
        y = x.right
        T2 = y.left
        y.left = x
        x.right = T2
        x.height = 1 + max(self.get_height(x.left), self.get_height(x.right))
        y.height = 1 + max(self.get_height(y.left), self.get_height(y.right))
        return y

    def insert(self, node, event_ID, start_time, end_time, event_name):
        if not node:
            return EventNode(event_ID, start_time, end_time, event_name)
        
        if start_time < node.start_time:
            node.left = self.insert(node.left, event_ID, start_time, end_time, event_name)
        else:
            node.right = self.insert(node.right, event_ID, start_time, end_time, event_name)

        node.height = 1 + max(self.get_height(node.left), self.get_height(node.right))
        balance = self.get_balance(node)

        if balance > 1 and start_time < node.left.start_time:
            return self.rotate_right(node)
        if balance < -1 and start_time > node.right.start_time:
            return self.rotate_left(node)
        if balance > 1 and start_time > node.left.start_time:
            node.left = self.rotate_left(node.left)
            return self.rotate_right(node)
        if balance < -1 and start_time < node.right.start_time:
            node.right = self.rotate_right(node.right)
            return self.rotate_left(node)

        return node

    def min_value_node(self, node):
        current = node
        while current.left:
            current = current.left
        return current

    def delete_by_start_time(self, node, start_time):
        if not node:
            return node

        if start_time < node.start_time:
            node.left = self.delete_by_start_time(node.left, start_time)
        elif start_time > node.start_time:
            node.right = self.delete_by_start_time(node.right, start_time)
        else:
            if node.left is None:
                return node.right
            elif node.right is None:
                return node.left
            temp = self.min_value_node(node.right)
            node.start_time = temp.start_time
            node.event_ID = temp.event_ID
            node.end_time = temp.end_time
            node.event_name = temp.event_name
            node.right = self.delete_by_start_time(node.right, temp.start_time)

        node.height = 1 + max(self.get_height(node.left), self.get_height(node.right))
        balance = self.get_balance(node)

        if balance > 1 and self.get_balance(node.left) >= 0:
            return self.rotate_right(node)
        if balance > 1 and self.get_balance(node.left) < 0:
            node.left = self.rotate_left(node.left)
            return self.rotate_right(node)
        if balance < -1 and self.get_balance(node.right) <= 0:
            return self.rotate_left(node)
        if balance < -1 and self.get_balance(node.right) > 0:
            node.right = self.rotate_right(node.right)
            return self.rotate_left(node)

        return node

    def search_by_id(self, node, event_id):
        if node is None:
            return None
        if node.event_ID == event_id:
            return node
        left_result = self.search_by_id(node.left, event_id)
        if left_result:
            return left_result
        return self.search_by_id(node.right, event_id)

    def search_range(self, node, start_range, end_range, results):
        if not node:
            return
        if start_range <= node.start_time <= end_range:
            results.append(node)
        if node.start_time > start_range:
            self.search_range(node.left, start_range, end_range, results)
        if node.start_time < end_range:
            self.search_range(node.right, start_range, end_range, results)

class EventManagementSystem:
    def __init__(self):
        self.tree = AVLTree()
        self.root = None

    def add_event(self, event_ID, start_time_str, end_time_str, event_name):
        try:
            start_time = datetime.datetime.strptime(start_time_str, "%d/%m/%Y %H:%M:%S")
            end_time = datetime.datetime.strptime(end_time_str, "%d/%m/%Y %H:%M:%S")
            existing_node = self.tree.search_by_id(self.root, event_ID)
            if existing_node:
                return f"Event ID {event_ID} already exists."
            self.root = self.tree.insert(self.root, event_ID, start_time, end_time, event_name)
            return f"ADDED: {event_ID} - {event_name}"
        except ValueError:
            return "Invalid date format. Please use dd/mm/yyyy hh:mm:ss."

    def remove_event(self, event_ID):
        try:
            event_ID = int(event_ID)
        except ValueError:
            return "Invalid Event ID"
        node = self.tree.search_by_id(self.root, event_ID)
        if not node:
            return "Event to be removed not found"
        self.root = self.tree.delete_by_start_time(self.root, node.start_time)
        return f"REMOVED: {event_ID} - {node.event_name}"

    def search_event(self, event_ID):
        try:
            event_ID = int(event_ID)
        except ValueError:
            return "Invalid Event ID"
        event = self.tree.search_by_id(self.root, event_ID)
        if event:
            separator = "-" * 90
            details = f"{event.event_ID} - {event.event_name} - {event.start_time.strftime('%d/%m/%Y %H:%M:%S')} - {event.end_time.strftime('%d/%m/%Y %H:%M:%S')}"
            return f"SEARCHED: {event_ID}\n{separator}\n{details}\n{separator}"
        else:
            return f"No event found with event ID {event_ID}"

    def search_event_by_range(self, start_range_str, end_range_str):
        try:
            start_range = datetime.datetime.strptime(start_range_str, "%d/%m/%Y %H:%M:%S")
            end_range = datetime.datetime.strptime(end_range_str, "%d/%m/%Y %H:%M:%S")
        except ValueError:
            return "Invalid date format. Please use dd/mm/yyyy hh:mm:ss."
        
        results = []
        self.tree.search_range(self.root, start_range, end_range, results)
        if not results:
            return f"No event found from {start_range.strftime('%d/%m/%Y %H:%M:%S')} to {end_range.strftime('%d/%m/%Y %H:%M:%S')}"
        
        header = f"SEARCHED: Events from {start_range.strftime('%d/%m/%Y %H:%M:%S')} to {end_range.strftime('%d/%m/%Y %H:%M:%S')}"
        separator = "-" * 90
        events = []
        for event in sorted(results, key=lambda x: x.start_time):
            event_line = f"{event.event_ID} - {event.event_name} - {event.start_time.strftime('%d/%m/%Y %H:%M:%S')} - {event.end_time.strftime('%d/%m/%Y %H:%M:%S')}"
            events.append(event_line)
        return f"{header}\n{separator}\n" + "\n".join(events) + f"\n{separator}"

    def process_input_file(self, input_file, output_file):
        with open(input_file, "r") as infile, open(output_file, "w") as outfile:
            for line in infile:
                line = line.strip()
                if not line:
                    continue
                if ": " not in line:
                    outfile.write("INVALID COMMAND\n")
                    continue
                command_part, param_str = line.split(": ", 1)
                params = [p.strip() for p in param_str.split(" - ")]
                command = command_part.strip()
                result = "INVALID COMMAND"
                try:
                    if command == "Add Event":
                        if len(params) != 4:
                            result = "INVALID COMMAND"
                        else:
                            event_id = int(params[0])
                            start_time = params[1]
                            end_time = params[2]
                            event_name = params[3]
                            result = self.add_event(event_id, start_time, end_time, event_name)
                    elif command == "Remove Event":
                        if len(params) != 1:
                            result = "INVALID COMMAND"
                        else:
                            event_id = params[0]
                            result = self.remove_event(event_id)
                    elif command == "Search Event by ID":
                        if len(params) != 1:
                            result = "INVALID COMMAND"
                        else:
                            event_id = params[0]
                            result = self.search_event(event_id)
                    elif command == "Search Event by Range":
                        if len(params) != 2:
                            result = "INVALID COMMAND"
                        else:
                            start_range = params[0]
                            end_range = params[1]
                            result = self.search_event_by_range(start_range, end_range)
                    else:
                        result = "INVALID COMMAND"
                except Exception as e:
                    result = f"ERROR: {str(e)}"
                outfile.write(result + "\n")

def main():
    event_system = EventManagementSystem()
    input_file = "inputPS04.txt"
    output_file = "outputPS04.txt"
    event_system.process_input_file(input_file, output_file)

if __name__ == "__main__":
    main()
