


def get_selected_vert_sequences(verts, ensure_seq_len=False, debug=False):

    sequences = []

    noncyclicstartverts = [v for v in verts if len([e for e in v.link_edges if e.select]) == 1]

    if noncyclicstartverts:
        v = noncyclicstartverts[0]

    else:
        v = verts[0]

    seq = []

    while verts:
        seq.append(v)

        if v not in verts:
            break

        else:
            verts.remove(v)

        if v in noncyclicstartverts:
            noncyclicstartverts.remove(v)

        nextv = [e.other_vert(v) for e in v.link_edges if e.select and e.other_vert(v) not in seq]

        if nextv:
            v = nextv[0]

        else:
            cyclic = True if len([e for e in v.link_edges if e.select]) == 2 else False

            sequences.append((seq, cyclic))

            if verts:
                if noncyclicstartverts:
                    v = noncyclicstartverts[0]
                else:
                    v = verts[0]

                seq = []

    if ensure_seq_len:
        seqs = []

        for seq, cyclic in sequences:
            if len(seq) > 1:
                seqs.append((seq, cyclic))

        sequences = seqs

    if debug:
        for seq, cyclic in sequences:
            print(cyclic, [v.index for v in seq])

    return sequences


def get_edges_vert_sequences(verts, edges, debug=False):
    sequences = []

    noncyclicstartverts = [v for v in verts if len([e for e in v.link_edges if e in edges]) == 1]

    if noncyclicstartverts:
        v = noncyclicstartverts[0]

    else:
        v = verts[0]

    seq = []

    while verts:
        seq.append(v)
        verts.remove(v)

        if v in noncyclicstartverts:
            noncyclicstartverts.remove(v)

        nextv = [e.other_vert(v) for e in v.link_edges if e in edges and e.other_vert(v) not in seq]

        if nextv:
            v = nextv[0]

        else:
            cyclic = True if len([e for e in v.link_edges if e in edges]) == 2 else False

            sequences.append((seq, cyclic))

            if verts:
                if noncyclicstartverts:
                    v = noncyclicstartverts[0]
                else:
                    v = verts[0]

                seq = []

    if debug:
        for verts, cyclic in sequences:
            print(cyclic, [v.index for v in verts])

    return sequences



def get_selection_islands(faces, debug=False):

    if debug:
        print("selected:", [f.index for f in faces])

    face_islands = []

    while faces:
        island = [faces[0]]
        foundmore = [faces[0]]

        if debug:
            print("island:", [f.index for f in island])
            print("foundmore:", [f.index for f in foundmore])

        while foundmore:
            for e in foundmore[0].edges:
                bf = [f for f in e.link_faces if f.select and f not in island]
                if bf:
                    island.append(bf[0])
                    foundmore.append(bf[0])

            if debug:
                print("popping", foundmore[0].index)

            foundmore.pop(0)

        face_islands.append(island)

        for f in island:
            faces.remove(f)

    if debug:
        print()
        for idx, island in enumerate(face_islands):
            print("island:", idx)
            print(" » ", ", ".join([str(f.index) for f in island]))


    islands = []

    for fi in face_islands:
        vi = set()
        ei = set()

        for f in fi:
            vi.update(f.verts)
            ei.update(f.edges)


        islands.append((list(vi), list(ei), fi))

    return sorted(islands, key=lambda x: len(x[2]), reverse=True)


def get_boundary_edges(faces, region_to_loop=False):

    boundary_edges = [e for f in faces for e in f.edges if (not e.is_manifold) or (any(not f.select for f in e.link_faces))]

    if region_to_loop:
        for f in faces:
            f.select_set(False)

        for e in boundary_edges:
            e.select_set(True)

    return boundary_edges
