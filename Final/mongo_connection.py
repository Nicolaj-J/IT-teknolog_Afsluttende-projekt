from pymongo import MongoClient
import gridfs
import datetime
import os


class mongodb_control():
    """
    Class to control mongodb
    costumer_name: any
    """
    def __init__(self) -> None:
        self.uri = "mongodb+srv://afsluttende-projekt.uik8oef.mongodb.net/?authSource=%24external&authMechanism=MONGODB-X509&retryWrites=true&w=majority"
        self.client = MongoClient(
            self.uri,
            tls=True,
            tlsCertificateKeyFile='/home/pi/Documents/final/mongodb_certificate/X509-cert-1903629998838294749.pem')
        self.db = self.client['Network_costumers']
        self.collection = self.db['Network_scans']
        self.date = datetime.datetime.now().strftime('%Y-%m-%d')
        self.current_folder = os.getcwd()

    def get_serial_number(self):
        """
        Makes a serial number and returns it
        -> str = serien number
        """
        serial_number = f"{datetime.datetime.now().year}{datetime.datetime.now().month}{datetime.datetime.now().day}{datetime.datetime.now().hour}{datetime.datetime.now().minute}{datetime.datetime.now().second}"
        return serial_number

    def json_upload(self,
                    local_scan={},
                    cloud_scan={},
                    costumer_name=""):
        """
        Uploads json file to mongodb
        local_scan: dict = any
        cloud_scan: dict = any
        """
        costumer_data = {
            "company_name": f"{costumer_name}",
            "date": self.date,
            "serial_number": self.get_serial_number(),
            "Local_scan": local_scan,
            "cloud_scan": cloud_scan
            }
        self.db.Network_scans.insert_one(costumer_data)

    def json_download(self):
        """
        Downloads json file from mongodb
        -> dict : json_data
        """
        collection = self.db['Network_scans']
        cursor = collection.find({})
        for document in cursor:
            json_data = document
            return json_data

    def get_all_json(self):
        """
        Gets costumer names and dates from all json files in Mongodb
        -> list = network_list
        """
        collection = self.db['Network_scans']
        cursor = collection.find({})
        network_list = []
        for document in cursor:
            network_list.append((document["company_name"],
                                 document["date"],
                                 document["serial_number"]))
        return network_list

    def docx_upload(self,
                    file_path=r"/home/pi/Documents/final/generated_report/network_scan.docx",
                    costumer_name=""):
        """
        Uploads a reports to mongodb
        file_path: str = r'/home/pi/Documents/final/generated_report/network_scan.docx'
        costumer_name: str = ''
        """
        file_data = open(file_path, "rb")
        data = file_data.read()
        fs = gridfs.GridFS(self.db)
        fs.put(data,
               costumer_name=costumer_name,
               date=self.date,
               serial_number=self.get_serial_number())

    def docx_download(self, serial_number):
        """
        Downloads docx file from mongodb
        seriel_number: any
        -> str(download_path)
        """
        fs = gridfs.GridFS(self.db)
        data = self.db.fs.files.find_one({"serial_number": serial_number})
        print(data)
        my_id = data["_id"]
        costumer_name = data["costumer_name"]
        date = data["date"]
        outputdata = fs.get(my_id).read()
        downloads_path = f"{self.current_folder}/file_to_send/{costumer_name}-{date}.docx"
        output = open(downloads_path, "wb")
        output.write(outputdata)
        output.close()
        return downloads_path

    def get_all_docx(self):
        """
        Gets all costumer names and dates from docx files in mongodb
        -> list = network_list
        """
        self.collection = self.db['fs.files']
        self.cursor = self.collection.find({})
        self.network_list = []
        for document in self.cursor:
            self.network_list.append((document["costumer_name"],
                                      document["date"],
                                      document["serial_number"]))
        return self.network_list
