# serve_build does not serve a browser leg's source map (debug-52, Order 52)

Repro (any workspace with a browser leg, debug preset):

    vilan build .            # writes dist/client.js + dist/client.js.map,
                             # client.js ends with //# sourceMappingURL=client.js.map
    vilan run .              # the server uses .serve_build(build_of("client"))
    curl -i http://127.0.0.1:<port>/client.js.map
    # -> falls through to the app's own handler (a SPA catch-all answers HTML),
    #    because LegBuild::artifacts (std/src/build.vl:72) lists the bundle,
    #    styles, chunks and assets - never the maps beside them.

DevTools then fails to load the map for a built (non-HMR) page. Under
`run --watch` with HMR this is sidestepped (E257 S6 names the map at the dev
channel, which serves it).
