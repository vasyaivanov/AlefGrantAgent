import sys; sys.path.insert(0, "/home/user/AlefGrantAgent/press_blast")
import email_template as T, gmail_sender as G
to = sys.argv[1]; name = sys.argv[2] if len(sys.argv) > 2 else "Jim"
m = G.build(to, T.SUBJECT, T.build_text(name), T.build_html(name), image_path=T.IMAGE_FILE, cid=T.IMAGE_CID)
print(G.send(m))
