
class ExamException(Exception):
    pass 


class CSVFile():

    def __init__(self, name=None):
        self.file_name = name

    def get_data(self):
        # Controllo che il nome del file sia una stringa
        if not isinstance(self.file_name, str):
            raise ExamException("Errore! Il nome del file deve essere una stringa.")
        
        # Controllo eisistenza e leggibilità del file
        try:
            # Provo ad aprire il file e leggerlo
            file = open(self.file_name,"r")
            file_content = file.read()
            file.close()
            # Ottengo le liste dei campi delle singole righe  
            processed_data = [line.strip().split(",") for line in file_content.split("\n")]
            
        except Exception as e:
            raise ExamException("Errore! {}".format(e))
        
        return processed_data


class CSVTimeSeriesFile(CSVFile):

    def __init__(self, name=None):
        super().__init__(name)

    def get_data(self):
        # Controllo che sia possible aprire il file
        try:
            file_content = super().get_data()
        except Exception as e:
            raise ExamException("Errore nell'apertura del file! {}".format(e))

        processed_data = []
        prev_epoch = 0
        
        for line_number, line in enumerate(file_content):
            # Controllo se la linea ha almeno due valori
            if len(line) < 2:
                continue
            
            epoch, temperature = line[:2]
            # Converto i dati del documento, salto quelli non convertibili
            try:
                curr_epoch = int(float(epoch))
                temperature = float(temperature)
            except:
               continue
            
            # Controllo se la serie è temporalmente ordinata
            if not prev_epoch < curr_epoch and not line_number == 0:
                raise ExamException("Errore! La serie temporale non è ordinata {} {}".format(prev_epoch, curr_epoch))
             
            prev_epoch = curr_epoch
            processed_data.append([curr_epoch, temperature])

        return processed_data


def utc_day(epoch):
    return epoch - (epoch % 86400) 


def compute_daily_max_difference(time_series):
    # Controllo se i dati siano una lista
    if not isinstance(time_series, list):
        raise ExamException("Errore! L'input deve essere una lista")
    
    # Non ci sono dati su cui calcolare l'escursionee
    if len(time_series) == 0:
        return []
    
    # Non posso calcolare l'escursione termica con un solo valore
    if len(time_series) == 1:
        return [None]
    
    # Inizializzo la prima giornata della serie ed 
    # il primo valore di temperatura per il ciclo
    current_day = utc_day(time_series[0][0])
    current_day_temperatures = [time_series[0][1]]
    processed_data = []
    
    for element in time_series[1:]:
        epoch, temperature = element
        # Se il giorno cambia
        if not utc_day(epoch) == current_day:
            # Se ho un solo valore
            if len(current_day_temperatures) == 1:
                processed_data.append(None)
            else:
                processed_data.append(max(current_day_temperatures) - min(current_day_temperatures))
            current_day = utc_day(epoch)
            current_day_temperatures = [temperature]
        
        # Se il giorno rimane lo stesso
        else:
            current_day_temperatures.append(temperature)     
    
    # Processo gli ultimi elementi della lista
    if current_day_temperatures != []:
        # Se ho un solo valore
        if len(current_day_temperatures) == 1:
            processed_data.append(None)
        else:
            processed_data.append(max(current_day_temperatures) - min(current_day_temperatures))

    return processed_data

print(compute_daily_max_difference(CSVTimeSeriesFile(name="data.csv").get_data()))