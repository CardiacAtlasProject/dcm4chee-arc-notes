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

import org.apache.log4j.Level;
import org.apache.log4j.Logger;

/**
 * 
 * @author Avan Suinesiaputra <avan.sp@gmail.com>
 *
 */
public class RetrieveSeries {
	
	// assume these settings
	private static final String calledAET = "DCM4CHEE";
	private static final String hostname = "localhost";
	private static final int port = 11112;
	
	private static final String patientID = "SCD0003001";
	private static final String studyInstanceUID = "2.16.124.113543.6006.99.3269191020737436947";
	
	public static void main(String[] args) throws Exception {
		
		Logger.getRootLogger().setLevel(Level.OFF);
		
		try {
			
			QueryDICOM qr = new QueryDICOM()
					.setCalledAET(calledAET)
					.setHostname(hostname)
					.setPort(port)
					.setRetrieveLevel(QueryDICOM.LevelType.SERIES)
					.addQueryAttribute("StudyInstanceUID", studyInstanceUID)
					.addQueryAttribute("PatientID", patientID);
			
			// let's return SeriesInstanceUID and SeriesDescription
			qr.addReturnAttributes("SeriesInstanceUID", "SeriesDescription");
			
			System.out.println("Attributes sent to SCP. Empty attributes are going to be returned by SCP.");
			System.out.println(qr.getKeys());
			
			System.out.println("Attributes returned by SCP:");
			qr.execute();
			
		} catch( Exception e ) {
            System.err.println("findscu: " + e.getMessage());
            e.printStackTrace();
            System.exit(2);
		}
		
	}	
	
}
