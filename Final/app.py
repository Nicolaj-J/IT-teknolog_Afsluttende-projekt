from flask import Flask, render_template, request, url_for, send_file
import os
import mongo_connection
import localscan
import cloud_scan
import network_diagram
import docx_creation
import time
app = Flask(__name__)


@app.route('/', methods=['POST', 'GET'])
def forside():
    """
    -> scan.html
    """
    return render_template('scan.html')


@app.route('/scan', methods=['POST', 'GET'])
def scan():
    """
    -> scan.html
    """
    if request.method == 'POST':

        options = {
            "company_name": request.form.get("customer"),
            "port_scan": 'ports' in request.form,
            "port_range": request.form.get("port-range"),
            "port_speed": request.form.get("port-speed"),
            "os_detection": 'os' in request.form,
            "own_ip": 'own-ip' in request.form,
            "exclude_other_ip": request.form.get("other-ip"),
            "client_id": request.form.get("client-id"),
            "tenant-id": request.form.get("tenant-id"),
            "secret-value": request.form.get("secret-value"),
            "subscription-id": request.form.get("subscription-id"),
        }
        if options["client_id"] != '' and options["tenant-id"] != '' and options['secret-value'] != '' and options['subscription-id'] != '':
            cloud_scan.export_azure_info(company_name=options['company_name'],
                                         client_id=options['client_id'],
                                         tentant=options["tenant-id"],
                                         secret=options["secret-value"],
                                         sub=options['subscription-id'])
            network_diagram.make_cloud_diagram(company_name=options['company_name'])
        localscan.network_scan(port_scan=bool(options['port_scan']),
                               port_range=options['port_range'],
                               port_scan_speed=options["port_speed"],
                               os_scan=bool(options["os_detection"]),
                               exclude_own_ip=bool(options['own_ip']),
                               company_name=options['company_name']
                               )
        time.sleep(0.5)
        network_diagram.make_local_diagram(company_name=options['company_name'])
        try:
            del(request.method)
        except:
            pass
        return render_template('scan.html')
    else:
        return render_template('scan.html')


@app.route('/eksport', methods=['POST', 'GET'])
def eksport():
    """
    -> eksport.html
    """
    json_files = os.listdir("/home/pi/Documents/final/scan-results")
    diagrams = os.listdir("/home/pi/Documents/final/network_diagrams")
    report_list = []
    for i in diagrams:
        for x in json_files:
            if i[0:-12] == x[0:-10]:
                report_list.append(i[0:-18])
    if request.method == 'POST':
        print("making report")
        company = request.form.get("report_company")
        print(company)
        docx_creation.report_generation(company_name=company)
        os.remove(f"/home/pi/Documents/final/network_diagrams/{company}_local_diagram.png")
        os.remove(f"/home/pi/Documents/final/scan-results/{company}_local_scan.json")
        try:
            os.remove(f"/home/pi/Documents/final/network_diagrams/{company}_cloud_diagram.png")
            os.remove(f"/home/pi/Documents/final/scan-results/{company}_cloud_scan.json")
        except:
            pass
        p1 = mongo_connection.mongodb_control()
        p1.docx_upload(file_path=f"/home/pi/Documents/final/generated_report/{company}_network_scan.docx", costumer_name=company)
        return render_template('eksport.html', reports=report_list)
    else:
        return render_template('eksport.html', reports=report_list)


@app.route('/database', methods=['POST', 'GET'])
def database():
    """
    -> database.html
    """
    for file in os.listdir(r"/home/pi/Documents/final/file_to_send"):
        os.remove(f"/home/pi/Documents/final/file_to_send/{file}")
    p1 = mongo_connection.mongodb_control()
    if request.method == 'POST':
        path = p1.docx_download(request.form.get("serienummer"))
        return send_file(path)
    else:
        return render_template('database.html', all_data=p1.get_all_docx())


if __name__ == '__main__':
    app.run(host="0.0.0.0")
