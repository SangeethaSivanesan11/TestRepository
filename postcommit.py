import mercurial, urllib, subprocess
from mercurial import util
from mercurial import patch
from mercurial.ui import ui
import json, os, inspect, sys, urllib2, httplib, datetime, re

from mercurial.localrepo import localrepository


repopath = sys.argv[1]
type = sys.argv[2]
if len(sys.argv) > 4:
	oldId = sys.argv[3]
	newId = sys.argv[4]
	branch = sys.argv[5]
elif len(sys.argv) > 3:
	st_changeset = sys.argv[3]
else:
	st_changeset = ""


COMMIT_TEMPLATE = 'LEGAL DECLARATION:I hereby ([^\n])*\n(LICENSE COMPATIBLE:([Yy][Ee][Ss]|[Nn][Oo]))*\n*'
OPTIONAL_TEMPLATE = 'IGNORE_ISSUECHECKS:YES(\n)*(I18N ISSUE ID :)*'

def getFileType(filename):
    values = filename.split('.')
    if len(values) > 1:
        return values[-1]
    else:
        return 'others'

def escapeChars(string):
    string = string.strip('\n').strip().strip('\\').strip('/')
    string = string.replace("\\", "\\\\").replace("'","\\'").replace("+", "\\+").replace("$", "\$")
    return string

def striplicense_template(logmsg):

    description = re.sub(COMMIT_TEMPLATE,'',logmsg)
    description = re.sub(OPTIONAL_TEMPLATE,'',description)
    description = escapeChars(description)
    return description

def addLogs(stringVal):
    print stringVal

def getCurrentTime():
    now = datetime.datetime.now()
    cur_time = now.strftime('%Y-%m-%d %H:%M:%S')
    return cur_time

def status_check(exec_command, exec_dir=None, background=False):

    if exec_dir:
        os.chdir(exec_dir)

    res = subprocess.Popen(exec_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if not background:
        result = res.communicate()
        return result

class HGRepository(object):

    def __init__(self, repo, ui):

        self.repo_type = 'HG'
        self.ui = ui
        self.repo = repo
        self.getStartChangeset()
        self.index_node = self.repo[self.node].parents()[0].hex()[0:11]
        self.module = os.path.basename(repo.root)
        self.branch = self.repo['tip'].branch()
        self.st_changeset = str(self.repo[self.node].rev()) + ":" + str(self.node)
        self.end_changeset = str(self.repo['tip'].rev()) + ":" + str(self.repo['tip'])
        self.commit_details = {}
        self.branch_details = {}
        self.diff_needed_files = {}
        self.diff_content = {}

    def getStartChangeset(self):
        if st_changeset != "":
            self.node = st_changeset
        else:
            self.node = -1
 
# 	***************************************************************************************************************
#	getCommits :
#
#			Initial method in this class to get commits,newchangesets json array
#
#			@param : 
#			
#			@return : {'commits': [{'files': {'Removed': [], 'Added': [{'AddedLines': '1', 'File': 'test',
#				   'RemovedLines': '0'}], 'Modified': []}, 'changeset': '3e4983962f67', 'parents': 
#				   'changed_lines': [1], 'file': 'test'}]}], 'user': 'gomathinayagam.d@zohocorp.com', 
#				   'branch': 'master', 'push_time': '2018-02-28 17:43:45', 'commit_type': 1, 
#				   'message': 'test', 'commit_date': '2018-02-28 17:43:21', 'revision': '3e49839'}], 
#				   'newchangesets': ['3e4983962f6743f1fc55ce53e62553a5f83524c8']}
#       						
#	*************************************************************************************************************** 
    def getCommits(self):

        files = []
        commits = []
        newchangesets = []
        if(len(self.repo) > 100):
            end_point = 100
        else:
            end_point = len(self.repo)
        for rev in xrange(self.repo[self.node].rev() + 1, end_point, 1):

            c = self.repo[rev]
            changeset = c.hex()[0:12]
            commit_date = util.datestr(c.date(), '%Y-%m-%d %H:%M:%S')
            parents = c.parents()
            branch = c.branch()
            changed_files = c.files()
            committed_user = c.user()
            description = c.description()
            newchangesets.append(changeset)

            commit = {'changeset' : changeset, 'branch' : branch, 'commit_date' : commit_date,
                      'message' : description, 'user' : committed_user, 'parents' : [],
                      'push_time': getCurrentTime()
                      }

	    #  diff_changes temporarly not going to be used *may* be useful in future (just add **self.getDiffContent(parent,node)** in diff_changes )
            for prchang in parents:
                parent_changeset = prchang.hex()[0:12]
                parent_branch = self.repo[parent_changeset].branch()
                commit['parents'].append({'changeset' :parent_changeset, 'branch' : parent_branch,
                                          'diff_changes' : ""})

            	if changed_files:
                	committed_files = list(self.status(parent_changeset, changeset))
                	committed_files[0] = list(set(committed_files[0]).intersection(set(changed_files)))
                	committed_files[1] = list(set(committed_files[1]).intersection(set(changed_files)))
                	committed_files[2] = list(set(committed_files[2]).intersection(set(changed_files)))
            	else:
                	committed_files = ([], [], [])

            	commit['files'] = {'Added': self.diffstat(parent_changeset,changeset,committed_files[1]), 'Modified': self.diffstat(parent_changeset,changeset,committed_files[0]), 'Removed': self.diffstat(parent_changeset,changeset,committed_files[2])}

            if len(commit['parents']) == 2:
                if commit['branch'] == commit['parents'][1]['branch']:
                    commit['commit_type'] = 3
                else:
                    commit['commit_type'] = 2
            else:
                commit['commit_type'] = 1

            commits.append(commit)
        commits.reverse()
        return commits, newchangesets

    def status(self, changeset1, changeset2):
        return self.repo.status(changeset1, changeset2, match=None)

    def getAddedFiles(self, branch):

        return self.repo.status(self.branch_details[branch]['parent'], branch, match=None)[1]

    def getModifedFiles(self, branch):

        return self.repo.status(self.branch_details[branch]['parent'], branch, match=None)[0]

    def getRemovedFiles(self, branch):

        return self.repo.status(self.branch_details[branch]['parent'], branch, match=None)[2]

    def getAllFiles(self, changeset):

        return self.repo[changeset].manifest().keys()

    def getChangeContext(self, changeset):

        return self.repo[changeset]

#	***************************************************************************************************************
#	getDiffOpts :
#
#			Provide extra options for diff command
#
#       *************************************************************************************************************** 
    def getDiffOpts(self):
        options = {'unified': '0', 'ignore_space_change': True, 'ignore_all_space': True}
        diffoptions = patch.diffopts(self.ui, options)
        return diffoptions

#	***************************************************************************************************************
#	getDiffContent :
#
#			Show changes between two changeset
#
#			@param : changeset1,changeset2
#			
#			@return : [{'changed_lines': [1,4,6], 'file': 'test'}]
#       *************************************************************************************************************** 
    def getDiffContent(self, changeset1, changeset2):
        diffcontent = []
        diffcontent = patch.diff(self.repo, changeset1, changeset2, opts=self.getDiffOpts())
        diffcontent = list(diffcontent)
        diff_changes = self.parseDiffContent(diffcontent)

        return diff_changes


#	***************************************************************************************************************
#	getDiffLines :
#
#			Find number of lines newly added in file
#
#			@param : changes
#
#			@return : [1,2,4,5]
#       ***************************************************************************************************************
    def getDiffLines(self,changes):
        difflines = []
        for val in changes:
            changed_line_values = str(val)

            if changed_line_values.find(',') > -1:
                start_linenumber = int(changed_line_values.split(',')[0])
                total_changed_lines = int(changed_line_values.split(',')[1])
                for line in range(start_linenumber, start_linenumber + total_changed_lines):
                    difflines.append(line)
            else:
                difflines.append(int(changed_line_values))

        return difflines

#       ***************************************************************************************************************
#	parseDiffContent :
#
#			Parse diff contents for two changesets
#
#			@param : diff
#			
#			@return : [{'changed_lines': [1,4,6], 'file': 'test'}]
#       *************************************************************************************************************** 
    def parseDiffContent(self, diff):
    
        diff_changes = []
        file_name = match_values = []
        for diff_content in diff:
            file_name_pattern = re.compile('^\\+\\+\\+ b/([^\\s]+)', re.M)
            modified_lines_pattern = re.compile('^@@[-0-9,\\s]+\\+([0-9+,]+)\\s*@@$', re.M)

            if not file_name:
                file_name = file_name_pattern.findall(diff_content)
            if not match_values:
                match_values = modified_lines_pattern.findall(diff_content)

            if file_name and match_values:
                file_name = file_name[0].replace('/', os.sep).strip()
                diff_changes.append({'file': file_name, 'changed_lines': self.getDiffLines(match_values)})
                file_name = match_values = []

        return diff_changes

# 	***************************************************************************************************************
#	difflist :
#
#			Try to get diff files list between two changesets
#
#			@param : rev1
#			@param : rev2
#			@param : files
#			
#			@return : [('README', 1, 0, False), ('testfile', 1, 0, False)]
#       						
#	****************************************************************************************************************

    def difflist(self, rev1, rev2, files=[], ignore_space=False, *pats, **opts):
        opts['stat'] = True
 
        if ignore_space:
            opts['ignore_space_change'] = True
            opts['ignore_all_space'] = True
            opts['ignore_blank_lines'] = True
 
        opts['rev'] = [str(rev1)+":"+str(rev2), ]
        diffopts = patch.diffopts(self.ui, opts)
        if files:
            file_list = (files,[],[])
            diff_content = patch.diff(self.repo, rev1, rev2, changes=file_list, opts=diffopts)
        else:
            diff_content = patch.diff(self.repo, rev1, rev2, opts=diffopts)
        diff_fileslist = patch.diffstatdata(util.iterlines(diff_content))
        return diff_fileslist

 
# 	***************************************************************************************************************
#	diffstat :
#
#			Return a files added,removed lines
#
#			@param : rev1
#			@param : rev2
#			@param : files
#			
#			@return :{'AddedLines': 1, 'File': 'testfile', 'RemovedLines': 0}
#       						
#	****************************************************************************************************************
    def diffstat(self, rev1, rev2, files, *pats, **opts):
	if files:
        	diff_fileslist = self.difflist(rev1, rev2, files, *pats, **opts)
		file_stat=[]
		for x in diff_fileslist:
			file_numstats = { 'File':[],'AddedLines':[],'RemovedLines':[] }
			file_numstats['File']=x[0]
			file_numstats['AddedLines']=x[1]
			file_numstats['RemovedLines']=x[2]
			file_stat.append(file_numstats)
		return file_stat
	return []
        


class GitRepository():

	def __init__(self, local_repository):
		self.logs = []
		self.module_dir = local_repository
        	self.oldId = oldId
        	self.newId = newId
        	self.branch = branch
        	self.module = os.path.basename(self.module_dir)
        	self.newchangesets = []
 
# 	***************************************************************************************************************
#	getCommits :
#
#			Initial method in this class to get commits,newchangesets json array
#
#			@param : 
#			
#			@return : {'commits': [{'files': {'Removed': [], 'Added': [{'AddedLines': '1', 'File': 'test',
#				   'RemovedLines': '0'}], 'Modified': []}, 'changeset': '3e4983962f67', 'parents': 
#				   'changed_lines': [1], 'file': 'test'}]}], 'user': 'gomathinayagam.d@zohocorp.com', 
#				   'branch': 'master', 'push_time': '2018-02-28 17:43:45', 'commit_type': 1, 
#				   'message': 'test', 'commit_date': '2018-02-28 17:43:21', 'revision': '3e49839'}], 
#				   'newchangesets': ['3e4983962f6743f1fc55ce53e62553a5f83524c8']}
#       						
#	*************************************************************************************************************** 

    	def getCommits(self):
       	 	self.branchlog(os.path.basename(self.branch),self.oldId,self.newId)
        	return self.logs, self.newchangesets

	
#       ***************************************************************************************************************
#	findNewBranchCommits :
#
#			Find number of commits present in inital branch creation
#
#			@param : changeset
#			@param : max_count
#			@param : skip
# 			@param : newId
#			@param : branchname
#			
#			@return : boolean       						
#	*************************************************************************************************************** 
	def findNewBranchCommits(self,changeset,max_count,skip,newId=None,branchname=None):
		cmd = "git rev-list --first-parent --max-count="+ str(max_count) + "--skip="+ str(skip) +" "+ newId
		validate = False
		rev_list = status_check(cmd,self.module_dir)
		rev_list = str(rev_list[0]).split('\n')
		rev_list = list(filter(None, rev_list))
		for x in rev_list:	 					# Iterate until branch base point
			rev_cmd = "git branch --contains " + x
			rev_cmd = status_check(rev_cmd,self.module_dir)
			rev_cmd = str(rev_cmd[0]).split('\n')
			if(len(rev_cmd) > 2): 
				validate = True
				break
			else:
				changeset.append(x)
		return validate

	
#       ***************************************************************************************************************
#	branchlog :
#		
#			Find a number of commits between tow changsets
#
#			@param : branchname
#			@param : oldId
#			@param : newId
#			
#			@return : None        						
#	*************************************************************************************************************** 
    	def branchlog(self, branchname=None, oldId=None,newId=None):
        	pretty_format = " --pretty='format:CMHash:%H %h##CMParent:%P##%p##CMAuthor:%an %ae##CMDate:%ci##CMMessage:%n%s%n%bLOGENDS'"
      	 	if oldId == "0000000000000000000000000000000000000000":
			changeset = []
			max_count = 50
			commit_count = 0
			skip = 0
			cmd = "git rev-list --count "+branchname
			commit_count = status_check(cmd,self.module_dir)
			commit_count = int(commit_count[0])
			if(commit_count < 50):
				max_count = commit_count
			while commit_count>=max_count:
				validate = self.findNewBranchCommits(changeset,max_count,skip,newId,branchname)
				if(validate):
					break
				max_count+=50
				skip+=50
			length = len(changeset)	
			if(length == 1):
           			cmd = "git log --numstat -1 " +  newId + pretty_format
			else:
				cmd = "git cat-file -p "+ changeset[length-1]
				parent_rev = status_check(cmd,self.module_dir)
				parent_rev = str(parent_rev[0]).split('\n')[1]
				parent_rev_pattern = re.compile('([a-z0-9]+)')
				result = parent_rev_pattern.findall(str(parent_rev))
				if(result[0] != "parent"):
					cmd = "git log --numstat " + changeset[0] + pretty_format
				else:
					cmd = "git log --numstat " +  changeset[length-1] + '~1..' + changeset[0] + pretty_format
		elif newId == "0000000000000000000000000000000000000000":
			cmd = ""			# For a branch deletion command statement is empty
		else:
			cmd = "git log --numstat " + oldId + '..' +  newId + pretty_format
        	commits = status_check(cmd, self.module_dir)
        	self.parseCommits(str(commits[0]), branchname)

	
#	***************************************************************************************************************
#	updateMergeDetails :
#
#			This method used to find how many files added,removed,modified in single changeset.Also it 
#			shows number of added and deleted lines in decimal notation for each files. 
#
#			@param : log
#			@param : parents
#			@param : parent_short
#			
#			@return : log         	
#					
#	*************************************************************************************************************** 
    	def updateMergeDetails(self, log, parents, parents_short):
        	log['is_merge'] = 1
        	log['merged_by'] = log['user']
        	log['parent2_branch'] = parents[1]
        	log['parent2']  = parents[1]
        	log['parent2_short']  = parents_short[1]
        	return log

	
#	***************************************************************************************************************
#	filestatus :
#
#			This method used to find how many files added,removed,modified in single changeset.Also it 
#			shows number of added and deleted lines in decimal notation for each files. 
#
#			@param : changeset
#			
#			@return : {'Removed': [], 'Added': [], 'Modified': [{'AddedLines': '1', 'File': 'test', 
#				'RemovedLines':'2'}]}         						
#	*************************************************************************************************************** 
    	def filestatus(self, changeset):
        	cmd = "git show --name-status --pretty='format:CMHash:%H' " + changeset
        	commit_info = status_check(cmd, self.module_dir)
        	commit_sts_pattern = re.compile('CMHash:([a-z0-9]+)\n+(([AMD]\s+(.*?)\n)*)?')
        	commit_sts_detail = commit_sts_pattern.findall(str(commit_info[0]))

        	result = {'Modified':[], 'Added': [], 'Removed':[]}

		cmd = "git show --numstat --pretty='format:CMHash:%H' " + changeset
		filter_info = status_check(cmd,self.module_dir)
		filter_sts_pattern = re.compile('CMHash:([a-z0-9]+)\n+(([0-9\-]+\s+[0-9\-]+\s+(.*?)\n)*)?')
		filter_sts_detail = filter_sts_pattern.findall(str(filter_info[0]))

		if commit_sts_detail:
           		commit_sts_detail = commit_sts_detail[0]
			filter_sts_detail = filter_sts_detail[0] 

		if commit_sts_detail:
            		if (commit_sts_detail[0] == changeset and commit_sts_detail[1] != ''):
               			changes = commit_sts_detail[1].strip('\n')
				filter_change = filter_sts_detail[1].strip('\n')
				filter_change = filter_change.split('\n')
				i = 0
                		for detail in changes.split('\n'):
                    			detail = detail.split('\t')
                   			status = detail[0]
                    			filename = escapeChars(detail[1])

					insertion_pattern = re.compile('([0-9\-]+)\t([0-9\-]+)')

					file_numstats = { 'File':[],'AddedLines':[],'RemovedLines':[] }

					num_stat = insertion_pattern.findall(filter_change[i])
					i = i+1
					file_numstats['File']=filename
					if num_stat:
						num_stat = num_stat[0]
						file_numstats['AddedLines']=num_stat[0]
						file_numstats['RemovedLines']=num_stat[1]
					else:
						file_numstats['AddedLines']=0
						file_numstats['RemovedLines']=0

                    			if status == 'A':
                      				result['Added'].append(file_numstats)
                    			elif status == 'M':
                        			result['Modified'].append(file_numstats)
                    			elif status == 'D':
                        			result['Removed'].append(file_numstats)

        	return result

	
#       ***************************************************************************************************************
#	parseCommits :
#
#			Find commits and newchangesets details
#
#			@param : commitlog,branch
#			
#			@return : None
#       ***************************************************************************************************************
    	def parseCommits(self, commitlog, branch):
        	commit_pattern = re.compile('CMHash:([a-z0-9]+) ([a-z0-9]+)##CMParent:([a-z0-9\s]+)?##([a-z0-9\s]+)?##CMAuthor:([a-zA-Z0-9.\-@+.\s]+)##CMDate:([0-9:\s+-]*)##CMMessage:\n*((?:.|\n)*?)\n*LOGENDS\n+(([0-9]+\s+(.*?)\n)*)?', re.DOTALL)
        	commits = commit_pattern.findall(commitlog)     	

        	for commit in commits:
           		node = commit[0]
            		revision = commit[1]
            		parents = commit[2].split(' ')
            		parents_short = commit[3].split(' ')
            		username = commit[4]
            		commit_date = re.sub('\+0530', '', commit[5]).strip()
            		description = striplicense_template(commit[6])
            		commited_files = commit[7].strip('\n').splitlines()
            		commit_type = 1
            		parentChangeset1 = parents[0]
            		parent1_branch = parents[0]
            		self.newchangesets.append(node)

            		log = {'changeset': node[:12], 'revision': revision, 'branch': branch, 'user': username,
                  	       'message': description, 'commit_type': commit_type, 'parents': [],
                   	       'commit_date': commit_date, 'push_time': getCurrentTime()
                   	      }  

			#  diff_changes temporarly not going to be used *may* be useful in future (just add **self.getDiffContent(parent,node)** in diff_changes )
            		for parent in parents:
                		log['parents'].append({'changeset' :parent[:12], 'branch' : parent[:12],
                                      		       'diff_changes' : ""})
            		if len(parents) == 2:
                		log = self.updateMergeDetails(log, parents, parents_short)
                		log['commit_type'] = 2

            		log['files'] = self.filestatus(node)
	    
	    		self.logs.append(log)

#	***************************************************************************************************************
#	getDiffContent :
#
#			Show changes between two changeset
#
#			@param : changeset1,changeset2
#			
#			@return : [{'changed_lines': [1,4,6], 'file': 'test'}]
#       *************************************************************************************************************** 

    	def getDiffContent(self, changeset1, changeset2):
        	diff_command = "git diff -U0 " + changeset1 + " " + changeset2 
        	result = status_check(diff_command, self.module_dir)
        	diff_changes = self.parseDiffContent(list(result))
        	return diff_changes


#	***************************************************************************************************************
#	getDiffLines :
#
#			Find number of lines newly added in file
#
#			@param : changes
#
#			@return : [1,2,4,5]
#       ***************************************************************************************************************
    	def getDiffLines(self,changes):
        	difflines = []
        	for val in changes:
            		changed_line_values = str(val)

            	if changed_line_values.find(',') > -1:
                	start_linenumber = int(changed_line_values.split(',')[0])
                	total_changed_lines = int(changed_line_values.split(',')[1])
                	for line in range(start_linenumber, start_linenumber + total_changed_lines):
                    		difflines.append(line)
            	else:
                	difflines.append(int(changed_line_values))

        	return difflines

#       ***************************************************************************************************************
#	parseDiffContent :
#
#			Parse diff contents for two changesets
#
#			@param : diff
#			
#			@return : [{'changed_lines': [1,4,6], 'file': 'test'}]
#       *************************************************************************************************************** 
    	def parseDiffContent(self, diff):
        	diff_changes = []
        	file_name = match_values = []
        	for diff_content in diff:
            		file_name_pattern = re.compile('^\\+\\+\\+ b/([^\\s]+)', re.M)
            		modified_lines_pattern = re.compile('^@@[-0-9,\\s]+\\+([0-9+,]+)\\s*@@', re.M)

            		if not file_name:
                		file_name = file_name_pattern.findall(diff_content)
            		if not match_values:
                		match_values = modified_lines_pattern.findall(diff_content)	

            		if file_name and match_values:
                		file_name = file_name[0].replace('/', os.sep).strip()
                		diff_changes.append({'file': file_name, 'changed_lines': self.getDiffLines(match_values)})
                		file_name = match_values = []

        	return diff_changes

result = {}
if type == "hg":
    repository = localrepository(ui(), repopath)
    hgObj = HGRepository(repository, ui())
    result['commits'], result['newchangesets'] = hgObj.getCommits()

else:
    gitObj = GitRepository(repopath)
    result['commits'], result['newchangesets'] = gitObj.getCommits()

print result
