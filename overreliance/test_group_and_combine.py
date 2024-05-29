def group_and_combine(lst):
    # Create a dictionary to group the strings by their scores
    score_dict = {}
    for score, string in lst:
        if score in score_dict:
            score_dict[score].append(string)
        else:
            score_dict[score] = [string]

    # Create a new list with summed scores and concatenated strings
    new_lst = []
    for score, strings in score_dict.items():
        combined_string = ' '.join(strings)
        new_lst.append([sum([score]), combined_string])

    return new_lst

# Example usage
original_list = [[4.0, 'brief history'], [4.0, 'periodic table'], [1.0, 'give'], [1.0, 'work'], [1.0, 'supposed'], [1.0, 'explain']]
result = group_and_combine(original_list)
print(result)