/* ***** BEGIN LICENSE BLOCK *****
 * Version: MPL 1.1/GPL 2.0/LGPL 2.1
 *
 * The contents of this file are subject to the Mozilla Public License Version
 * 1.1 (the "License"); you may not use this file except in compliance with
 * the License. You may obtain a copy of the License at
 * http://www.mozilla.org/MPL/
 *
 * Software distributed under the License is distributed on an "AS IS" basis,
 * WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
 * for the specific language governing rights and limitations under the
 * License.
 *
 * The Original Code is part of dcm4che, an implementation of DICOM(TM) in
 * Java(TM), hosted at https://github.com/gunterze/dcm4che.
 *
 * The Initial Developer of the Original Code is
 * Agfa Healthcare.
 * Portions created by the Initial Developer are Copyright (C) 2011
 * the Initial Developer. All Rights Reserved.
 *
 * Contributor(s):
 * See @authors listed below
 *
 * Alternatively, the contents of this file may be used under the terms of
 * either the GNU General Public License Version 2 or later (the "GPL"), or
 * the GNU Lesser General Public License Version 2.1 or later (the "LGPL"),
 * in which case the provisions of the GPL or the LGPL are applicable instead
 * of those above. If you wish to allow use of your version of this file only
 * under the terms of either the GPL or the LGPL, and not to allow others to
 * use your version of this file under the terms of the MPL, indicate your
 * decision by deleting the provisions above and replace them with the notice
 * and other provisions required by the GPL or the LGPL. If you do not delete
 * the provisions above, a recipient may use your version of this file under
 * the terms of any one of the MPL, the GPL or the LGPL.
 *
 * ***** END LICENSE BLOCK ***** */

package org.cardiacatlas.dicom;

import java.io.IOException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;

import org.dcm4che3.data.UID;
import org.dcm4che3.net.Priority;
import org.dcm4che3.net.pdu.PresentationContext;
import org.dcm4che3.tool.common.CLIUtils;
import org.dcm4che3.tool.findscu.FindSCU;

/**
 * 
 * A simple query DICOM class that runs the C-FIND command using the FindSCU class.
 * 
 * @author Avan Suinesiaputra <avan.sp@gmail.com>
 *
 */
public class QueryDICOM extends FindSCU {
	
	private ExecutorService executorService;
	private ScheduledExecutorService scheduledExecutorService;
	
	// always use Patient->Study->Series->CompositeObject structure
	private final String cuid = UID.PatientRootQueryRetrieveInformationModelFIND;
	
	public enum LevelType { PATIENT, STUDY, SERIES, IMAGE };
	
	public QueryDICOM() throws IOException {
		super();
		
        this.executorService = Executors.newSingleThreadExecutor();
        this.scheduledExecutorService = Executors.newSingleThreadScheduledExecutor();

        this.getDevice().setExecutor(executorService);
        this.getDevice().setScheduledExecutor(scheduledExecutorService);
        
        // set information model
        String[] IVR_LE_FIRST = {
                UID.ImplicitVRLittleEndian,
                UID.ExplicitVRLittleEndian,
                UID.ExplicitVRBigEndianRetired
            };
        this.getAAssociateRQ().addPresentationContext(new PresentationContext(1, this.cuid, IVR_LE_FIRST));
        
        
	}
	
	public QueryDICOM setRetrieveLevel(LevelType _level) {
		this.addLevel(_level.toString());
		return this;
	}
	
	public String getCuid() {
		return this.cuid;
	}

	public QueryDICOM setCalledAET(String calledAET) {
		this.getAAssociateRQ().setCalledAET(calledAET);
		return this;
	}
	
	public QueryDICOM setHostname(String hostname) {
		this.getRemoteConnection().setHostname(hostname);
		return this;
	}
	
	public QueryDICOM setPort(int port) {
		this.getRemoteConnection().setPort(port);
		return this;
	}
	
	public QueryDICOM addQueryAttribute(String tagString, String value) {
		
		int[] tags = {CLIUtils.toTag(tagString)};
		CLIUtils.addAttributes(this.getKeys(), tags, value);
		
		return this;
	}
	
	public QueryDICOM addReturnAttributes(String...attrs) {
		CLIUtils.addEmptyAttributes(this.getKeys(), attrs);
		
		return this;
	}
		
	public void execute() throws Exception, IOException {
		try {
			
			this.open();
			
			DICOMTransferHandler handler = new DICOMTransferHandler(this.getAssociation());
			this.getAssociation().cfind(cuid, Priority.NORMAL, this.getKeys(), null, handler);
			
			
		} finally {
			this.close();
			this.executorService.shutdown();
			this.scheduledExecutorService.shutdown();
		}
	}
	
}
