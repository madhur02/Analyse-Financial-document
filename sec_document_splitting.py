def extracted_content(file_buffers):
    buffer_10k = []
    flag_10k = False

    for line in file_buffers:
        line = line.lower()
        if line.find('<type>10-k') != -1:
            flag_10k = True
            buffer_10k.append('<document>')
            buffer_10k.append(line)

        elif (line.find('</DOCUMENT>') != -1) and flag_10k == True:
            flag_10k = False
            buffer_10k.append(line)

        elif flag_10k == True:
            buffer_10k.append(line)
    data_content = "".join(buffer_10k)
    f = open("demo.html",'w')
    f.write(data_content)
    f.close()



def processing_header(header_content):
    header_dict = {}
    for line in header_content:
        header_info = line.split(":")
        header_info = list(map(lambda x: x.strip('\n').strip('\t'),header_info))
        header_info = [header for header in header_info if header]
        if len(header_info) >1:
            header_dict[header_info[0]] = "@@".join(header_info[1:])
    return header_dict

def parse_txt(txt_file):
    content = open(txt_file).readlines()
    header_content = []
    header_flag    = False
    for line in content[:60]:
        line = line.lower()
        if line.find('<SEC-HEADER')!= -1 or line.find('<sec-header')!= -1:
            header_flag = True
            header_content.append(line)
        elif (line.find('</SEC-HEADER')!= -1 or line.find('</sec-header')!= -1) and header_flag:
            header_content.append(line)
            header_flag = False
        elif header_flag:
            header_content.append(line)
    processing_header(header_content)
    extracted_content(content)



file_name = "demo.txt"
parse_txt(file_name)
