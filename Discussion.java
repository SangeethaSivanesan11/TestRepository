//$Id$
package com.zoho.code.repository;

import java.util.logging.Logger;

import com.zoho.cide.mail.EMail;
import com.zoho.cide.mail.Mailer;
import com.zoho.cide.mail.TransmailUtil;
import com.zoho.cide.user.UserAPI;

import java.util.logging.Level;

import org.json.JSONObject;

public class Discussion {
	
    private String filePath;
    private String note;
    private int noteType;
    private int targetType;
    private String targetId;
    private int lineType;
    private int viewMode;
    private int oldLine;
    private int newLine;
    private Long cideAccountId;
    private Long repositoryId;
    private Long repositoryFileId;
    public static final Logger LOGGER = Logger.getLogger(Discussion.class.getName());

    public void setFilePath(String filePath){
        this.filePath = filePath;
    }
    
    public void setNote(String message){
        this.note = message;
    }

    public void setNoteType(String noteType){
    	this.noteType = getNoteTypeValue(noteType).getTypeId();
    }
    
    public void setTargetType(String targetType){
        this.targetType = getTargetTypeValue(targetType).getTypeId();
    }
    
    public void setTargetId(String targetId){
        this.targetId = targetId;
    }
    
    public void setLineType(String lineType){
        System.out.println("test repo");
        this.lineType =  getLineTypeValue(lineType).getTypeId();
    }
    
    public void setViewMode(String viewMode){
        this.viewMode =  getViewModeValue(viewMode).getTypeId();
    }
    
    public void setOldLine(int oldLine){
        this.oldLine = oldLine;
    }
    
    public void setNewLine(int newLine){
        this.newLine = newLine;
    }
    
    public void setUserId(long cideAccountId) {
        this.cideAccountId = cideAccountId;
    }
    
    public void setRepositoryId(long repositoryId) {
        this.repositoryId = repositoryId;
    }
    
    public void setRepositoryFileId(Long repositoryFileId) {
        this.repositoryFileId = repositoryFileId;
    }
    
    public String getFilePath(){
       return filePath;
    }
    
    public String getNote(){
       return note;
    }

    public int getNoteType(){
       return noteType;
    }
    
    public int getTargetType(){
        return targetType;
    }
    
    public String getTargetId(){
        return targetId;
    }
    
    public int getLineType(){
        return lineType;
    }
    
    public int getViewMode(){
       return viewMode;
    }
    
    public int getOldLine(){
        return oldLine;
    }
    
    public int getNewLine(){
       return newLine;
    }

    public Long getUserId() {
        return cideAccountId;
    }

    public Long getRepositoryId() {
        return repositoryId;
    }
    
    public Long getRepositoryFileId() {
        return repositoryFileId;
    }
	public enum TargetType {
    	MERGE_REQUEST(1,"merge_request"),
        COMMIT(2,"commits"),
        ISSUE(3,"issue"),
        PROJECT_SNIPPET(4,"project_snippet"),
    	COMMENT(2,"comment"),
    	REPLY(1,"reply"),
    	ALL(2,"all");
    	
        private int type;
        private String state;

        TargetType(int type,String state) {
            this.type = type;
            this.state=state;
        }
        public TargetType getProjectType() {
            return this;
        }
        public int getTypeId() {
            return this.type;
        }
        public String getTypeString() {
            return this.state;
        }
    }

	public static TargetType getTargetTypeValue(String state) {
        for(TargetType request: TargetType.values()) {
            if(request.getTypeString().equals(state)) {
                return request;
            }
        }
        return null;
    }
	
	public static TargetType getTargetTypeId(int typeId) {
        for(TargetType request: TargetType.values()) {
            if(request.getTypeId() == typeId) {
                return request;
            }
        }
        return null;
    }
	
	public enum LineType {
    	OLD(1,"old"),
    	NEW(2,"new");
    	
        private int type;
        private String state;

        LineType(int type,String state) {
            this.type = type;
            this.state=state;
        }
        public LineType getProjectType() {
            return this;
        }
        public int getTypeId() {
            return this.type;
        }
        public String getTypeString() {
            return this.state;
        }
    }
	
	public static LineType getLineTypeValue(String state) {
        for(LineType type: LineType.values()) {
            if(type.getTypeString().equals(state)) {
                return type;
            }
        }
        return null;
    }
	
	public static LineType getLineTypeId(int typeId) {
        for(LineType type: LineType.values()) {
            if(type.getTypeId() == typeId) {
                return type;
            }
        }
        return null;
    }
	
	public enum NoteType {
    	DIFFNOTE(1,"diff_note"),
    	DISCUSSION_NOTE(2,"discussion_note");
    	
        private int type;
        private String state;

        NoteType(int type,String state) {
            this.type = type;
            this.state=state;
        }
        public NoteType getProjectType() {
            return this;
        }
        public int getTypeId() {
            return this.type;
        }
        public String getTypeString() {
            return this.state;
        }
    }
	
	public static NoteType getNoteTypeValue(String state) {
        for(NoteType type: NoteType.values()) {
            if(type.getTypeString().equals(state)) {
                return type;
            }
        }
        return null;
    }
	
	public static NoteType getNoteTypeId(int typeId) {
        for(NoteType type: NoteType.values()) {
            if(type.getTypeId() == typeId) {
                return type;
            }
        }
        return null;
    }
	
	public enum ViewMode {
    	INLINE(1,"inline"),
    	PARALLEL(2,"parallel");
    	
        private int type;
        private String state;

        ViewMode(int type,String state) {
            this.type = type;
            this.state=state;
        }
        public ViewMode getProjectType() {
            return this;
        }
        public int getTypeId() {
            return this.type;
        }
        public String getTypeString() {
            return this.state;
        }
    }
	
	public static ViewMode getViewModeValue(String state) {
        for(ViewMode type: ViewMode.values()) {
            if(type.getTypeString().equals(state)) {
                return type;
            }
        }
        return null;
    }
	
	public static ViewMode getViewModeId(int typeId) {
        for(ViewMode type: ViewMode.values()) {
            if(type.getTypeId() == typeId) {
                return type;
            }
        }
        return null;
    }
	
	public enum Comment {
    	COMMENT(2,"comment"),
    	REPLY(1,"reply"),
    	ALL(2,"all");
    	
        private int type;
        private String state;

        Comment(int type,String state) {
            this.type = type;
            this.state=state;
        }
        public Comment getProjectType() {
            return this;
        }
        public int getTypeId() {
            return this.type;
        }
        public String getTypeString() {
            return this.state;
        }
    }
	
	public static void sentDiscussionMail(Long cideAccId, String status, String note) throws Exception {
		JSONObject userObj = UserAPI.getUserInfo(cideAccId);
		String senderName = userObj.getString("email");
		String subject = senderName + " started a discussion" + status;
		EMail notificationMail = new EMail(userObj.getString("email"), "sangeetha.sivanesan");
		notificationMail.setSenderName(userObj.getString("fullname"));
		notificationMail.setSubject(subject);
		notificationMail.setHTML("");
		notificationMail.setTag(TransmailUtil.NOTIFICATION_TAG);
		try {
			Mailer.sendMail(notificationMail);
		} catch (Exception e) {
			LOGGER.log(Level.SEVERE, "Error while sending mail :: ", e);
		}
	}
	
}
