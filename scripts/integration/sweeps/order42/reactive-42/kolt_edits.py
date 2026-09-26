# The A124 S2c edits for kolt (reactive-42), applied to a COPY. Each is (file, exact old, exact new).
import sys, os
root = sys.argv[1]
EDITS = [
 ("src/lib/overlay.vl", "\t\tself.scrims.map(|count| count > 0)\n", "\t\tself.scrims.map(|count| count > 0).cell()\n"),
 ("src/model.vl", "\t\t\t.get_or(id, || get_client().map_safe(|client| client.get_channel_name(id)))\n\t\t\t.map(|x| x.unwrap_or_default())\n",
                  "\t\t\t.get_or(id, || get_client().map_safe(|client| client.get_channel_name(id)))\n\t\t\t.map(|x| x.unwrap_or_default())\n\t\t\t.cell()\n"),
 ("src/model.vl", "\t\t\t.get_or(id, || get_client().map_safe(|client| client.get_messages(id)))\n\t\t\t.map(|x| x.unwrap_or_default())\n",
                  "\t\t\t.get_or(id, || get_client().map_safe(|client| client.get_messages(id)))\n\t\t\t.map(|x| x.unwrap_or_default())\n\t\t\t.cell()\n"),
 ("src/model.vl", "\t\tget_client().map_safe(|client| client.get_channels()).map(|x| x.unwrap_or_default())\n",
                  "\t\tget_client().map_safe(|client| client.get_channels()).map(|x| x.unwrap_or_default()).cell()\n"),
 ("src/model.vl", "\t\t\t.map(|x| x.flatten()))\n", "\t\t\t.map(|x| x.flatten())\n\t\t\t.cell())\n"),
 ("src/model.vl", "\t\tself.map(|x| x.map(transform)).flatten().map(|x| x.flatten())\n", "\t\tself.map(|x| x.map(transform)).flatten().map(|x| x.flatten()).cell()\n"),
 ("src/lib/storage.vl", "\t\tself.signal.map(transform)\n", "\t\tself.signal.map(transform).cell()\n"),
 ("src/store.vl", "\t\tself.global_store.channels.map(|x| x.keys())\n", "\t\tself.global_store.channels.map(|x| x.keys()).cell()\n"),
 ("src/store.vl", "\t\tself.global_store.channels.map(|x| x.get(channel).map(|record| Channel { id = record.id }))\n",
                  "\t\tself.global_store.channels.map(|x| x.get(channel).map(|record| Channel { id = record.id })).cell()\n"),
 ("src/store.vl", "\t\tself.global_store.messages.map(|x| x.get(message))\n", "\t\tself.global_store.messages.map(|x| x.get(message)).cell()\n"),
 ("src/channel.vl", "\t(source.map(|(a, _)| a), source.map(|(_, b)| b))\n", "\t(source.map(|(a, _)| a).cell(), source.map(|(_, b)| b).cell())\n"),
 ("src/client.vl", "\t\t\t.map(|path| Route::from_segments(segments(path)));\n", "\t\t\t.map(|path| Route::from_segments(segments(path)))\n\t\t\t.cell();\n"),
 ("src/lib/search.vl", "\t\t\t\t.enumerate()\n\t\t\t\t.to_list()),\n", "\t\t\t\t.enumerate()\n\t\t\t\t.to_list())\n\t\t\t\t.cell(),\n"),
 ("src/lib/search.vl", "\t\t\ttable\n\t\t});\n\t\tSearchable { list, table }\n", "\t\t\ttable\n\t\t}).cell();\n\t\tSearchable { list, table }\n"),
]
for path, old, new in EDITS:
    full = os.path.join(root, path)
    text = open(full).read()
    n = text.count(old)
    if n != 1:
        sys.exit(f"{path}: expected exactly one match, found {n}: {old!r}")
    open(full, "w").write(text.replace(old, new))
print(f"{len(EDITS)} edits applied")
