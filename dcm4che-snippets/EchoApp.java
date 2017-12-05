import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;

import org.apache.log4j.Level;
import org.apache.log4j.Logger;
import org.dcm4che3.data.Attributes;
import org.dcm4che3.net.ApplicationEntity;
import org.dcm4che3.net.Connection;
import org.dcm4che3.net.Device;
import org.dcm4che3.tool.storescu.StoreSCU;

/**
 * EchoApp: implements C-ECHO connection
 * 
 * @author: Avan Suinesiaputra
 */
public class EchoApp 
{
    private static final String calledAET = "DCM4CHEE";
    private static final String hostname = "localhost";
    private static final int port = 11112;
	
    public static void main( String[] args )
    {
        Logger.getRootLogger().setLevel(Level.OFF);
    	
        try {
            // create SCU
            ApplicationEntity ae = new ApplicationEntity("STORESCU");            
            Connection conn = new Connection();
            Device device = new Device("storescu");
            
            device.addApplicationEntity(ae);
            device.addConnection(conn);
            ae.addConnection(conn);
        		
            // create StoreSCU object
            StoreSCU storeSCU = new StoreSCU(ae);
        		
            // configure remote connection and associate request
            storeSCU.getAAssociateRQ().setCalledAET(calledAET);
            storeSCU.getRemoteConnection().setHostname(hostname);
            storeSCU.getRemoteConnection().setPort(port);
        		
            ExecutorService executorService = Executors.newSingleThreadExecutor();
            device.setExecutor(executorService);
        		
            ScheduledExecutorService scheduledExecutorService = Executors.newSingleThreadScheduledExecutor();
            device.setScheduledExecutor(scheduledExecutorService);
        		
            try {
                storeSCU.open();
                Attributes attr = storeSCU.echo();
                System.out.println(attr.toString());
            } finally {
                storeSCU.close();
            }	
        		
        } catch( Exception e ) {
            System.out.println("Error: " + e.getMessage() );	
        }
        
    }
	
}
