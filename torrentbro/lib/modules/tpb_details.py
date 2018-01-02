# TPB Module to fetch torrent details
# Details are saved in a custom HTML page
# HTML files are saved in ~/.torrench/temp directory
# HTML files can be cleared with (-c) argument [To be used with -t ]

from bs4 import BeautifulSoup
import requests
import os
import time
import platform
import io

home = os.path.expanduser(os.path.join('~', '.torrench'))
temp_dir = os.path.expanduser(os.path.join(home, 'temp'))

if platform.system() == 'Windows':
    charset = ""
else:
    charset = "<meta charset='utf-8'>"


def get_details(url, index):
    initial_time = time.time()
    raw = requests.get(url)
    initial_end_time = time.time() - initial_time
    raw = raw.content
    unique_id = url.split('/')[-1]
    soup = BeautifulSoup(raw, "lxml")

    content = soup.find('div', id="details")
    nfo = str(content.find_all('div', class_="nfo")[0])
    dt = content.find_all('dt')  # Torrent info table headers
    dd = content.find_all('dd')  # info table values
    title = "(Index: " + index + ") - " + str(soup.find('div', id="title").string)
    name = str(soup.find('div', id="title"))
    magnet = soup.find('div', class_="download").a["href"]

    # FETCHING COMMENTS
    comments_list = []
    commenter_list = []

    # Fetching comments of base (default) page
    comments = soup.find_all('div', class_='comment')
    commenter = soup.find(id="comments").find_all('p')
    comments_list.append(comments)
    commenter_list.append(commenter)

    # Determine if any other comment pages are present.
    total_comments_pages = soup.find('div', class_='browse-coms')  # Total number of comment pages
    opt = ''
    total_time = 0
    if total_comments_pages is not None:
        total_comments_pages = int(soup.find('div', class_='browse-coms').strong.string)
        print("\n%d comment pages (1 page = 25 comments (MAX))" % (total_comments_pages))
        temp = True
        pg_count = 0
        if(total_comments_pages > 2):  # If more than 3 comment pages are present, ask user what to do.
            while(temp):
                opt = input("Fetch all pages? May take longer [y/n/display anyway[d]]: ")
                if opt == 'y' or opt == 'Y':
                    pg_count = 0
                    temp = False
                elif opt == 'n' or opt == 'N':
                    pg_inp = input("Number of pages to fetch comments from? [0 < n < %d]: " % (total_comments_pages));
                    if pg_inp == '':
                        print("Bad Input")
                    else:
                        pg_inp = int(pg_inp)
                        if pg_inp < total_comments_pages and pg_inp > 0:
                            pg_count = total_comments_pages - pg_inp
                            temp = False
                        else:
                            print("Bad Input")
                elif opt == 'd' or opt == 'D':
                    pg_count = total_comments_pages
                    temp = False
                else:
                    print("Bad Input")

        print("\nLast page (%d) [Already fetched]" % (total_comments_pages))
        total_comments_pages -= 1  # Since last page is already fetched. So start from (n-1)th page

        while(total_comments_pages > pg_count):
            start_time = time.time()
            raw = requests.get(url, params={'page': total_comments_pages})
            end_time = time.time() - start_time
            print("Page " + str(total_comments_pages) + " [%.2f sec]" % (end_time))
            raw = raw.content
            soup2 = BeautifulSoup(raw, "lxml")
            comments = soup2.find_all('div', class_='comment')
            commenter = soup2.find(id="comments").find_all('p')
            comments_list.append(comments)
            commenter_list.append(commenter)
            total_time += end_time
            total_comments_pages -= 1

    torrent_hash = soup.find('div', class_="download").a["href"].split('&')[0].split(':')[-1]
    torrent_hash = torrent_hash.upper()

    # Set torrent hash explicitly as it is not fetched directly as other dd elements
    dd[-1].string = torrent_hash

    # Check Uploader-Status
    style_tag = "<style> pre {white-space: pre-wrap; text-align: left} h2, .center {text-align: center;} .vip {color: #32CD32} .trusted {color: #FF00CC}  body {margin:0 auto; width:70%;} table, td, th {border: 1px solid black;} td, th {text-align: center; vertical-align: middle; font-size: 15px; padding: 6px} .boxed{border: 1px solid black; padding: 3px} </style> "
    begin_tags = "<!DOCTYPE html><html><head>" + charset + "<meta http-equiv='Content-type'> <title>" + title + "</title>" + style_tag + "</head><body>"
    end_tags = "</body></html>"

    # File opens here
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    html_file = os.path.join(temp_dir, unique_id + ".html")
    f = io.open(html_file, "w", encoding="utf-8")
    f.write(begin_tags)
    f.write("<h2><u><a href=" + url + " target='_blank'>" + name + "</a></u></h2><br />")
    f.write("<table align='center'>")

    # Torrent info table
    for i in dt:
        dt_str = str(i.get_text()).replace(":", "")
        f.write("<th>" + dt_str + "</th>")
    f.write("</tr>\n<tr>\n")
    status = ""
    for j in dd:
        dd_str = str(j.get_text()).replace(":", "")
        if j.img is not None:
            if j.img['title'] == 'VIP':
                dd_str = "<div class='vip'>" + dd_str + "</div>"
                status = 'vip'
            elif j.img['title'] == 'Trusted':
                dd_str = "<div class='trusted'>" + dd_str + "</div>"
                status = 'trusted'
        f.write("<td>" + dd_str + "</td>")
    f.write("</tr></table>")

    if status == 'vip':
        f.write("<div class='vip'> *VIP Uploader </div>")
    elif status == 'trusted':
        f.write("<div class='trusted'> *Trusted Uploader </div>")

    f.write("<br />")

    # Magnetic link[1]
    f.write("<div class='center'><a href=" + magnet + " target='_blank'>[Magnetic Link (Download)]</a></div><br />")

    # Printing Description
    f.write("<div class='boxed'>")
    f.write("<h2><u> DESCRIPTION </u></h2>")
    f.write("<pre>")
    f.write(nfo)
    f.write("</pre></div>")
    f.write("<div class='boxed'>")
    f.write("<h2><u> COMMENTS </u></h2>")
    # End Description

    count = 0

    # Printing Comments
    if commenter_list != [] and commenter_list[0] != []:
        f.write("<table align='center'>")
        for k in range(len(commenter_list)):
            for i, j in zip(commenter_list[k], comments_list[k]):
                f.write("<tr><th>" + str(i.get_text()) + "</th>")
                f.write("<td><pre>" + str(j.get_text()) + "</pre></td></tr>")
                count += 1
        f.write("<div class=center> (Total %d comments) </div><br />" % (count))
        f.write("</table><br />")
        f.write("<div class=center> (Total %d comments) </div><br />" % (count))

    else:
        f.write("<pre class='center'>No comments found!</pre></div>")
    f.write("</div><br />")
    # End Comments

    # Magnetic link[2]
    f.write(end_tags)
    f.write("<br /><div class='center'><a href=" + magnet + " target='_blank'>[Magnetic Link (Download)]</a></div><br /><br />")
    f.close()

    file_url = "file://" + html_file
    if opt == 'd' or opt == 'D' or opt == '':
        print("\n[in %.2f sec]" % (initial_end_time))
    else:
        print("\n[in %.2f sec]" % (total_time))
    return file_url


if __name__ == "__main__":
    print("It's a module. Can only be imported!")
