#Program to solve Ariadnes Thread Task set by iwoca
#Alex Amato
#v1.0

import cmath
import requests #Python package used to interrogate API
import json

#Lists to document companies and officers so they aren't duplicated
listOfUsedCompanies = []
listOfUsedOfficers = []

#Depth of search i.e. 0 - base company, 1: 1 level of companies, 2: 2 levels of companies... etc
maxDepth = 1

#Company, CompanyID, Depth, Score Structures to build visual list
compStruct = []
compIDStruct = []
depthStruct = []
compStructScoreSing = []
compStructScore = []

#Used for scoring
currentYear = 2021

#Used for failed request
maxCount = 10

#API Key
CompHouseAPIKey = "7DxApniADg6MjZ6bbIjrdi0FfuU6KVX3P_m8iaQi"

"""FUNCTIONS"""
#Function to provide Company snapshot given a company number
def get_company_info(companyNum, urlLink=""):
    urlBegin = "https://api.companieshouse.gov.uk/company/"
    urlFinal = urlBegin + companyNum + urlLink
    responseApi = requests.get(urlFinal, auth = (CompHouseAPIKey,""))
    count = 0
    #Repeats request if not completed
    while count < maxCount:
        if str(responseApi) != '<Response [200]>':
            responseApi = requests.get(urlFinal, auth = (CompHouseAPIKey,""))

        else:
            break
        count += 1
        print("Request Failed. Trying again...")
        #print(responseApi)
    #json used to provide readable data
    response = responseApi.json()
    del responseApi
    return response

#Function to provide officer snapshot given an officer link
def get_officer_info(officerLink):
    urlBegin = "https://api.companieshouse.gov.uk/officers"
    urlFinal = urlBegin + officerLink + "/appointments"
    responseApi = requests.get(urlFinal, auth = (CompHouseAPIKey,""))
    count = 0
    #Repeats request if not completed
    while count < maxCount:
        if str(responseApi) != '<Response [200]>':
            responseApi = requests.get(urlFinal, auth = (CompHouseAPIKey,""))

        else:
            break
        count += 1
        print("Request Failed. Trying again...")
    response = responseApi.json()
    del responseApi
    return response

#Function to retrieve name of company from a given company number
def get_company_name_from_number(companyNum):
    urlBegin = "https://api.companieshouse.gov.uk/company/"
    urlFinal = urlBegin + companyNum 
    responseApi = requests.get(urlFinal, auth = (CompHouseAPIKey,""))
    count = 0
    while count < maxCount:
        if str(responseApi) != '<Response [200]>':
            responseApi = requests.get(urlFinal, auth = (CompHouseAPIKey,""))
        else:
            break
        count += 1
        print("Request failed. Trying again...")
    response = responseApi.json()
    del responseApi
    compName = response['company_name']
    del response
    return compName

#Function to build company hierarchy structure given a company number input and a configurable depth of search
def get_associated_companies_info_by_company(companyNum, depth, maxDepth=2):
    #Bool variables to check if company/officer is repeated
    officerClash = False
    companyClash = False

    compName = get_company_name_from_number(companyNum)
    #print(depth * "-" + str(depth) + compName + str(depth) + str(maxDepth))
    #Appends necessary details to lists used to build hierarchy structure
    depthStruct.append(depth)
    compStruct.append(compName)
    compIDStruct.append(companyNum)
    compStructScoreSing.append(compute_company_score(companyNum))
    
    #Checks if hierarchy structure is required
    if maxDepth > 0:
        if depth < maxDepth * 2: #depth stopping condition
            officers = get_list_of_officer_IDs_from_company(companyNum)
            depth += 1
            for i in range(len(officers[0])): # For each officer related to a specific company
                officerClash = False
                #Check to see if officer has appeared before
                for x in range(len(listOfUsedOfficers)):
                    if officers[0][i] == listOfUsedOfficers[x]:
                        officerClash = True
                if officerClash == True: # Writes in officer if there is a clash, for visualisation, but doesn't probe any further
                    officerClash = False
                    #print((depth) * "-" + str(depth) + str(officers[1][i]))
                    depthStruct.append(depth)
                    compStruct.append(officers[1][i])
                    compIDStruct.append("")
                    compStructScoreSing.append("")
                else:
                    #print((depth) * "-" + str(depth) + str(officers[1][i]))
                    #Appends officer details to hierarchy list
                    depthStruct.append(depth)
                    compStruct.append(officers[1][i])
                    compIDStruct.append("")
                    compStructScoreSing.append("")
                    companies = get_list_of_companies_from_officer(officers[0][i])
                    listOfUsedOfficers.append(officers[0][i]) # Updates used officers
                    depth += 1
                    for j in range(min(len(companies[0]),10)): #for each company related to officer
                        companyClash = False
                        #Check to see if company has appeared before
                        for y in range(len(listOfUsedCompanies)):
                            if companies[1][j] == listOfUsedCompanies[y]:
                                companyClash = True
                        if companyClash == True: # Appends company if used for visual purpose but doesnt probe further
                            companyClash == False
                            #print(depth * "-" + str(depth) + str(companies[0][j]) + str(depth) + str(maxDepth))
                            depthStruct.append(depth)
                            compStruct.append(companies[0][j])
                            compIDStruct.append(companies[1][j])
                            compStructScoreSing.append(compute_company_score(companies[1][j]))
                        else:
                            listOfUsedCompanies.append(companies[1][j])
                            #Calls function again on new company
                            get_associated_companies_info_by_company(companies[1][j], depth, maxDepth)
                    depth -= 1
        else:
            depth -= 1
    else:
        return compName
    
#Function to retieve related officer names and links given a company number
def get_list_of_officer_IDs_from_company(companyNum):
    urlBegin = "https://api.companieshouse.gov.uk/company/"
    urlFinal = urlBegin + companyNum + "/officers"
    responseApi = requests.get(urlFinal, auth = (CompHouseAPIKey,""))
    count = 0
    while count < maxCount:
        if str(responseApi) != '<Response [200]>':
            responseApi = requests.get(urlFinal, auth = (CompHouseAPIKey,""))
        else:
            break
        count += 1
        print("Request failed. Trying again...")
    response = responseApi.json()
    del responseApi
    response = response['items']
    officerLinks = []
    officerNames = []
    #creates lists of officer names and links 
    for x in response:
        if 'resigned_on' not in x:
            officerLinks.append(x['links']['officer']['appointments'])
            officerNames.append(x['name'])
    del response
    #print(officerLinks)
    return officerLinks, officerNames

#Function to retrieve a list of company names and numbers from an officer link
def get_list_of_companies_from_officer(officerLink):
    urlBegin = "https://api.companieshouse.gov.uk"
    urlFinal = urlBegin + officerLink
    responseApi = requests.get(urlFinal, auth = (CompHouseAPIKey,""))
    count = 0
    while count < maxCount:
        if str(responseApi) != '<Response [200]>':
            responseApi = requests.get(urlFinal, auth = (CompHouseAPIKey,""))
        else:
            break
        count += 1
        print("Request failed. Trying again...")
    response = responseApi.json()
    name = response['name']
    del responseApi
    companyNames = []
    companyIDs = []
    #Creates lists of company names and IDs
    for i in range(len(response['items'])):
        companyNames.append(response['items'][i]['appointed_to']['company_name'])
        companyIDs.append(response['items'][i]['appointed_to']['company_number'])
    del response
    return companyNames, companyIDs, name

#Function to build company hierarchy structure given an officer link input
def get_associated_companies_info_by_officer(officerLink):
    #First retrieves related companies
    companyNames, companyIDs, officerName = get_list_of_companies_from_officer("/officers" + officerLink + "/appointments")
    del companyNames
    #Appends necessary lists for hierarchy structure
    depthStruct.append(0)
    compStruct.append(officerName)
    compIDStruct.append("")
    compStructScoreSing.append("")
    listOfUsedOfficers.append("/officers" + officerLink + "/appointments")
    #Calls original company structure function on each company - essentially building individual structure underneath the officer in question
    for i in range(len(companyIDs)):
        listOfUsedCompanies.append(companyIDs[i])
        get_associated_companies_info_by_company(companyIDs[i], 1, maxDepth)

#Function to compute company score based on company number alone
def compute_company_score(companyNum):
    compInfo = get_company_info(companyNum)
    #Starting Score
    score = 100
    #Determines age of company. Companies with age < 5 years are penalised
    if compInfo['date_of_creation'] != "":
        yearCreated = int(compInfo['date_of_creation'][0:4])
    else:
        yearCreated = 0
    
    if compInfo['company_status'] != 'active': #Checks company is actually doing business currently
        score -= 100
        return score 
    else:
        if compInfo['has_charges'] == True: #Charges used as penalties
            numCharges = get_num_of_company_charges(companyNum)
        else:
            numCharges = 0
        if compInfo['has_insolvency_history'] == True: #Insolvency cases used as penalties
            numCases = get_num_of_company_insolvency(companyNum)
        else:
            numCases = 0
        if yearCreated >= currentYear - 5:
            yearPen = 5 - (currentYear - yearCreated)
        else:
            yearPen = 0
        score -= numCharges * 2
        score -= (numCases ** 2) * 5
        score -= yearPen * 5
        return score

#Function to retrieve number of company charges
def get_num_of_company_charges(companyNum):
    response = get_company_info(companyNum, "/charges")
    #Prevents error if company has no charges info
    if response != None and response:
        numCharges = response['total_count']
        return numCharges
    else:
        return 0

#Function to retrieve number of company insolvency cases
def get_num_of_company_insolvency(companyNum):
    response = get_company_info(companyNum, "/insolvency")
    #Prevents error if company has no insolvency info
    if response != None and response:
        numCases = len(response['cases'])
        return numCases
    else:
        return 0

#Function to compute company score based on company hierarchy
def compute_company_structure_score(companyNum):
    #Builds basic hierarchy
    get_associated_companies_info_by_company(companyNum, 0, maxDepth)
    for i in range(len(depthStruct)):
        if compIDStruct[i] != "":
            compStructScore.append(compute_company_score(compIDStruct[i]))
        else:
            compStructScore.append("")

    #Computes company Score based on structure
    for i in range(len(compStructScore)):
        if depthStruct[i] == 0:
            total_score = compStructScore[i] # Initial company Score
        elif compStructScore[i] != "":
            total_score = total_score - (total_score - compStructScore[i]) / ((depthStruct[i] / 2 + 1) * 10) # Weighted scores for related companies
    total_score = round(total_score,2)
    return total_score
    
#Function to print out company hierarchy in format specified in README
def print_company_structure():
    print("There are " + str(len(depthStruct)) + " entities in this diagram.")
    for i in range(len(depthStruct)):
        print(depthStruct[i]*"  " + str(compIDStruct[i]) + " " + compStruct[i] + " " + str(compStructScoreSing[i])) # + ": " + compIDStruct[i])
    
#Function to check a given company number is valid
def check_company_number(companyNum):
    compCheckTest = get_company_info(companyNum)
    compCheck = False
    #Check to see if response returned is an error 
    try:
        compCheckTest['errors']
        #getattr(compCheckTest, 'errors')
        compCheck = True
    except KeyError:
        compCheck = False
    return compCheck

"""BODY"""

#Interface Code
print("Welcome to the Ariadnes Thread Solution. Please enter the number of the option you would like to carry out:")
print("1: Create a company structure graph from a given company")
print("2: Create a company structure graph from a given officer")
print("3: Compute a company score using the company structure")
print("4: Retrieve company Info")
option = input()
if option == "1": 
    print("Please enter the company number of the company you'd like to start the search from: e.g. 07798925")
    inputCompNum = input()
    listOfUsedCompanies.append(inputCompNum) #Adds company ID to list of used companies to avoid duplication
    #Check company number is valid or whether company inofrmation is empty
    compCheck = check_company_number(inputCompNum)
    if get_company_info(inputCompNum) == {} or compCheck == True:
        print("That is not a valid company number. Please try again.")
    else:
        print("Please enter the depth level you would like: (0 - base company, 1 - first related companies, 2 - second related companies... etc")
        maxDepth = int(input())
        get_associated_companies_info_by_company(inputCompNum, 0, maxDepth)
        print_company_structure()
elif option == "2":
    print("Please enter the officer appointment link (don't forget the slash at the beginning!): e.g. /Y-7-tBrvzDw7tplKHhkcX4x8N-M")
    inputOfficerLink = input()
    #Check officer link is valid
    if get_officer_info(inputOfficerLink) == {}:
        print("That is not a valid officer appointment link. Please try again.")
    else:
        print("Please enter the depth level you would like: (0 - base companies from Officer, 1 - Next related companies1... etc")
        maxDepth = int(input())
        get_associated_companies_info_by_officer(inputOfficerLink)
        print_company_structure()
elif option == "3":
    print("Please enter the company number of the company you'd like to score: e.g. 07798925 ")
    inputCompNum = input()
    #Check company number is valid or whether company inofrmation is empty
    compCheck = check_company_number(inputCompNum)
    if get_company_info(inputCompNum) == {} or compCheck == True:
        print("That is not a valid company number. Please try again.")
    else:
        compScore = compute_company_structure_score(inputCompNum)
        print("The company score is: " + str(compScore))
elif option == "4":
    print("Please enter the company number of the company you'd like to get information for: e.g. 07798925 ")
    inputCompNum = input()
    #Check company number is valid or whether company inofrmation is empty
    compCheck = check_company_number(inputCompNum)
    if get_company_info(inputCompNum) == {} or compCheck == True:
        print("That is not a valid company number. Please try again.")
    else:
        compInfo = get_company_info(inputCompNum)
        print("Here is the company snapshot for " + compInfo['company_name'] + ": ")
        for i in compInfo: # Prints company snapshot
            print(i + ": " + str(compInfo[i]))
else:
    print("Sorry, that appears to be an invalid input. Please try again.")
    
