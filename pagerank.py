def page_rank(links, num_iterations=20, initial_pr=1.0):
    from collections import defaultdict
    import numpy as np

    page_rank = defaultdict(lambda: float(initial_pr))
    num_outgoing_links = defaultdict(float)
    incoming_link_sets = defaultdict(set)
    incoming_links = defaultdict(lambda: np.array([]))
    damping_factor = 0.85

    for (from_id, to_id) in links:
        num_outgoing_links[int(from_id)] += 1.0
        incoming_link_sets[to_id].add(int(from_id))

    for link in links:
        if link[1] not in num_outgoing_links:
            num_outgoing_links[int(link[1])] = 1.0

    for doc_id in incoming_link_sets:
        incoming_links[doc_id] = np.array([from_doc_id for from_doc_id in incoming_link_sets[doc_id]])

    num_documents = float(len(num_outgoing_links))
    lead = (1.0 - damping_factor) / num_documents
    partial_PR = np.vectorize(lambda doc_id: page_rank[doc_id] / num_outgoing_links[doc_id])

    for i in range(num_iterations):
        for doc_id in num_outgoing_links:
            tail = 0.0
            if len(incoming_links[doc_id]):
                tail = damping_factor * partial_PR(incoming_links[doc_id]).sum()
            page_rank[doc_id] = lead + tail

    return page_rank

if __name__ == "__main__":
    print(page_rank([(1,2), (2, 4), (4, 3)]))
    print(page_rank([(1,2), (2, 4), (4, 3), (3, 1), (3, 2)]))