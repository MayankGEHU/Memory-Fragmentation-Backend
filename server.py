from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Resettable memory blocks (template)
MEMORY_TEMPLATE = [
    {"size": 100, "allocated": None},
    {"size": 200, "allocated": None},
    {"size": 300, "allocated": None},
    {"size": 400, "allocated": None},
    {"size": 500, "allocated": None},
    {"size": 600, "allocated": None},
    {"size": 700, "allocated": None},
    {"size": 800, "allocated": None},
    {"size": 900, "allocated": None},
    {"size": 1000, "allocated": None},
]

# Clone memory on each allocation
def reset_memory():
    return [dict(block) for block in MEMORY_TEMPLATE]

@app.route('/api/allocate_memory', methods=['POST'])
def allocate_memory():
    allocation_data = request.get_json()

    if not allocation_data:
        return jsonify({"error": "No allocation data provided"}), 400
    
    algorithm = allocation_data[0].get('algorithm', 'firstFit')
    memory_blocks = reset_memory()
    allocation_info = []

    def first_fit(proc):
        for i, block in enumerate(memory_blocks):
            if block['allocated'] is None and block['size'] >= proc['size']:
                return i
        return None

    def best_fit(proc):
        best_index = None
        min_diff = float('inf')
        for i, block in enumerate(memory_blocks):
            if block['allocated'] is None and block['size'] >= proc['size']:
                diff = block['size'] - proc['size']
                if diff < min_diff:
                    min_diff = diff
                    best_index = i
        return best_index

    def worst_fit(proc):
        worst_index = None
        max_diff = -1
        for i, block in enumerate(memory_blocks):
            if block['allocated'] is None and block['size'] >= proc['size']:
                diff = block['size'] - proc['size']
                if diff > max_diff:
                    max_diff = diff
                    worst_index = i
        return worst_index

    # Run allocation for each process
    for proc in allocation_data:
        pid = proc['pid']
        size = proc['size']

        if algorithm == 'firstFit':
            index = first_fit(proc)
        elif algorithm == 'bestFit':
            index = best_fit(proc)
        elif algorithm == 'worstFit':
            index = worst_fit(proc)
        else:
            return jsonify({"error": f"Unknown algorithm: {algorithm}"}), 400

        if index is not None:
            block = memory_blocks[index]
            block['allocated'] = size
            allocation_info.append({
                "pid": pid,
                "blockIndex": index,
                "used": size,
                "totalBlock": block['size'],
                "internalFragmentation": block['size'] - size
            })
        else:
            allocation_info.append({
                "pid": pid,
                "message": "No suitable block found for allocation"
            })

    return jsonify({
        "memoryBlocks": memory_blocks,
        "allocationInfo": allocation_info
    })

if __name__ == '__main__':
    app.run(debug=True)
